import 'dart:async';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'auth_service.dart';
import 'token_storage.dart';
import '../api/api_exception.dart';

enum AuthStatus {
  initial,
  unauthenticated,
  authenticating,
  authenticated,
  updateRequired,
  error,
}

class AuthState extends ChangeNotifier {
  final AuthService _authService;
  final TokenStorage _tokenStorage;

  AuthStatus _status = AuthStatus.initial;
  String? _role;
  String? _errorMessage;

  // Fires every 5 days while the app is open so the 7-day server token
  // is always refreshed before it expires.
  Timer? _refreshTimer;

  AuthStatus get status => _status;
  String? get role => _role;
  String? get errorMessage => _errorMessage;

  AuthState({
    required AuthService authService,
    required TokenStorage tokenStorage,
  })  : _authService = authService,
        _tokenStorage = tokenStorage;

  // ── Public API ─────────────────────────────────────────────────────────────

  /// Initializes the auth state by checking for an existing token.
  Future<void> initialize() async {
    final token = await _tokenStorage.getToken();
    if (token != null && token.isNotEmpty) {
      await _fetchRoleAndAuthenticate();
    } else {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  /// Attempts to log in with an activation key.
  Future<bool> login(String activationKey) async {
    _setStatus(AuthStatus.authenticating);
    try {
      final result = await _authService.activate(activationKey);
      await _tokenStorage.saveToken(result['token'] as String);
      final expiresAt = result['expires_at'];
      if (expiresAt is DateTime) {
        await _tokenStorage.saveExpiresAt(expiresAt);
      }
      return await _fetchRoleAndAuthenticate();
    } on ApiException catch (e) {
      _setError(e.message);
      return false;
    } catch (e) {
      _setError('An unexpected error occurred.');
      return false;
    }
  }

  /// Logs the user out and clears all local auth state.
  Future<void> logout() async {
    _stopRefreshTimer();
    _setStatus(AuthStatus.authenticating);
    await _authService.logout();
    await _tokenStorage.deleteToken();
    await _tokenStorage.deleteExpiresAt();
    _role = null;
    _setStatus(AuthStatus.unauthenticated);
  }

  // ── Core Auth Flow ─────────────────────────────────────────────────────────

  Future<bool> _fetchRoleAndAuthenticate() async {
    try {
      _role = await _authService.getMe();

      // Perform version check (Admins are exempt so they can fix settings)
      bool isVersionValid = true;
      if (_role != 'ADMIN') {
        final packageInfo = await PackageInfo.fromPlatform();
        isVersionValid = await _authService.checkVersion(packageInfo.version);
      }

      if (!isVersionValid) {
        _setStatus(AuthStatus.updateRequired);
        return false;
      }

      _setStatus(AuthStatus.authenticated);
      _startRefreshTimer();
      return true;

    } on UnauthorizedException {
      // ── FIX: A single 401 is NOT enough to wipe the token. ──────────────
      // The server may have briefly restarted, been deployed, or a proxy
      // may have timed out the request. Retry once after a short delay
      // before concluding the token is genuinely revoked.
      return await _retryAfterUnauthorized();

    } catch (_) {
      // Transient error (network down, server unreachable, timeout, etc).
      // Keep the token — the user should not have to re-enter the activation
      // key just because they have no internet connection right now.
      _setError('Unable to connect. Please check your connection and try again.');
      return false;
    }
  }

  /// Retries /auth/me once (with a 3-second delay) after receiving a 401.
  /// Only wipes the token if the retry also fails with 401.
  Future<bool> _retryAfterUnauthorized() async {
    await Future.delayed(const Duration(seconds: 3));
    try {
      _role = await _authService.getMe();

      // Retry succeeded — server was just temporarily unavailable.
      bool isVersionValid = true;
      if (_role != 'ADMIN') {
        final packageInfo = await PackageInfo.fromPlatform();
        isVersionValid = await _authService.checkVersion(packageInfo.version);
      }
      
      if (!isVersionValid) {
        _setStatus(AuthStatus.updateRequired);
        return false;
      }

      _setStatus(AuthStatus.authenticated);
      _startRefreshTimer();
      return true;

    } on UnauthorizedException {
      // Two consecutive 401s — the token is genuinely revoked or invalid.
      // Only now do we wipe it and force re-activation.
      await _tokenStorage.deleteToken();
      await _tokenStorage.deleteExpiresAt();
      _role = null;
      _setStatus(AuthStatus.unauthenticated);
      return false;

    } catch (_) {
      // Retry also hit a transient error (network, timeout).
      // Keep the token — the user may reconnect and retry manually.
      _setError('Unable to connect. Please check your connection and try again.');
      return false;
    }
  }

  // ── Proactive Token Refresh Timer ──────────────────────────────────────────

  /// Starts a periodic timer that silently calls /auth/me every 5 days while
  /// the app is open. This keeps the 7-day backend token alive as long as the
  /// app is used at least once a week.
  void _startRefreshTimer() {
    _stopRefreshTimer();
    _refreshTimer = Timer.periodic(const Duration(days: 5), (_) async {
      if (_status == AuthStatus.authenticated) {
        try {
          await _authService.getMe();
          // The ApiClient automatically saves any X-Session-Token / 
          // X-Session-Expires-At headers returned, so no extra work needed.
        } catch (_) {
          // Ignore failures in the background refresh — the next foreground
          // call or the next timer tick will retry.
        }
      }
    });
  }

  void _stopRefreshTimer() {
    _refreshTimer?.cancel();
    _refreshTimer = null;
  }

  // ── Internal Helpers ───────────────────────────────────────────────────────

  void _setStatus(AuthStatus status) {
    _status = status;
    if (status != AuthStatus.error) {
      _errorMessage = null;
    }
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    _status = AuthStatus.error;
    notifyListeners();
  }

  void clearError() {
    if (_status == AuthStatus.error) {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  @override
  void dispose() {
    _stopRefreshTimer();
    super.dispose();
  }
}
