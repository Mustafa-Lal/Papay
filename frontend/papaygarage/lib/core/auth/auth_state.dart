import 'package:flutter/material.dart';
import 'auth_service.dart';
import 'token_storage.dart';
import '../api/api_exception.dart';

enum AuthStatus {
  initial,
  unauthenticated,
  authenticating,
  authenticated,
  error,
}

class AuthState extends ChangeNotifier {
  final AuthService _authService;
  final TokenStorage _tokenStorage;

  AuthStatus _status = AuthStatus.initial;
  String? _role;
  String? _errorMessage;

  AuthStatus get status => _status;
  String? get role => _role;
  String? get errorMessage => _errorMessage;

  AuthState({
    required AuthService authService,
    required TokenStorage tokenStorage,
  })  : _authService = authService,
        _tokenStorage = tokenStorage;

  /// Initializes the auth state by checking for an existing token
  Future<void> initialize() async {
    final token = await _tokenStorage.getToken();
    if (token != null && token.isNotEmpty) {
      await _fetchRoleAndAuthenticate();
    } else {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  /// Attempts to log in with an activation key
  Future<bool> login(String activationKey) async {
    _setStatus(AuthStatus.authenticating);
    try {
      final token = await _authService.activate(activationKey);
      await _tokenStorage.saveToken(token);
      return await _fetchRoleAndAuthenticate();
    } on ApiException catch (e) {
      _setError(e.message);
      return false;
    } catch (e) {
      _setError('An unexpected error occurred.');
      return false;
    }
  }

  /// Logs the user out
  Future<void> logout() async {
    _setStatus(AuthStatus.authenticating);
    await _authService.logout();
    await _tokenStorage.deleteToken();
    _role = null;
    _setStatus(AuthStatus.unauthenticated);
  }

  Future<bool> _fetchRoleAndAuthenticate() async {
    try {
      _role = await _authService.getMe();
      _setStatus(AuthStatus.authenticated);
      return true;
    } catch (e) {
      // If fetching 'me' fails, the token is likely invalid or expired.
      await _tokenStorage.deleteToken();
      _role = null;
      _setStatus(AuthStatus.unauthenticated);
      return false;
    }
  }

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
}
