import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  final FlutterSecureStorage _storage;
  static const String _tokenKey = 'session_token';
  static const String _expiresAtKey = 'session_expires_at';

  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  // ── Token ──────────────────────────────────────────────────────────────────

  Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<void> deleteToken() async {
    await _storage.delete(key: _tokenKey);
  }

  // ── Expiry ─────────────────────────────────────────────────────────────────

  Future<void> saveExpiresAt(DateTime expiresAt) async {
    await _storage.write(key: _expiresAtKey, value: expiresAt.toIso8601String());
  }

  Future<DateTime?> getExpiresAt() async {
    final value = await _storage.read(key: _expiresAtKey);
    if (value == null) return null;
    return DateTime.tryParse(value);
  }

  Future<void> deleteExpiresAt() async {
    await _storage.delete(key: _expiresAtKey);
  }
}
