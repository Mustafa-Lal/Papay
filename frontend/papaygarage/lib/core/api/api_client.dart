import 'dart:convert';
import 'package:http/http.dart' as http;
import '../auth/token_storage.dart';
import 'api_endpoints.dart';
import 'api_exception.dart';

class ApiClient {
  final TokenStorage _tokenStorage;
  final http.Client _client;

  ApiClient({
    required TokenStorage tokenStorage,
    http.Client? client,
  })  : _tokenStorage = tokenStorage,
        _client = client ?? http.Client();

  /// Perform a GET request
  Future<dynamic> get(String endpoint, {Map<String, String>? queryParameters}) async {
    final uri = _buildUri(endpoint, queryParameters);
    final headers = await buildHeaders();
    
    try {
      final response = await _client.get(uri, headers: headers);
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  /// Perform a POST request
  Future<dynamic> post(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    try {
      final response = await _client.post(
        uri,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  /// Perform a POST multipart request (for file uploads)
  Future<dynamic> postMultipart(
    String endpoint, {
    required String fileField,
    required String filename,
    required List<int> bytes,
    Map<String, String>? fields,
  }) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    final request = http.MultipartRequest('POST', uri);
    headers.remove('Content-Type');
    request.headers.addAll(headers);

    if (fields != null) {
      request.fields.addAll(fields);
    }

    request.files.add(http.MultipartFile.fromBytes(
      fileField,
      bytes,
      filename: filename,
    ));

    try {
      final streamedResponse = await _client.send(request);
      final response = await http.Response.fromStream(streamedResponse);
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  /// Perform a PUT request
  Future<dynamic> put(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    try {
      final response = await _client.put(
        uri,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  /// Perform a PATCH request
  Future<dynamic> patch(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    try {
      final response = await _client.patch(
        uri,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      );
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  /// Perform a DELETE request
  Future<dynamic> delete(String endpoint) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    try {
      final response = await _client.delete(uri, headers: headers);
      await _handleSessionRefresh(response);
      return _processResponse(response);
    } catch (e) {
      _handleNetworkError(e);
    }
  }

  // --- Internal Helpers ---

  Uri _buildUri(String endpoint, [Map<String, String>? queryParameters]) {
    final baseUri = Uri.parse(ApiEndpoints.baseUrl);
    return Uri(
      scheme: baseUri.scheme,
      host: baseUri.host,
      port: baseUri.port,
      path: endpoint,
      queryParameters: queryParameters,
    );
  }

  Future<Map<String, String>> buildHeaders() async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    final token = await _tokenStorage.getToken();
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    
    return headers;
  }

  /// Extracts the new token from the response headers if the session was renewed.
  /// Also persists the updated expiry time when provided by the backend.
  Future<void> _handleSessionRefresh(http.Response response) async {
    final newToken = response.headers['x-session-token'];
    if (newToken != null && newToken.isNotEmpty) {
      await _tokenStorage.saveToken(newToken);
      final expiresAtHeader = response.headers['x-session-expires-at'];
      if (expiresAtHeader != null && expiresAtHeader.isNotEmpty) {
        final expiresAt = DateTime.tryParse(expiresAtHeader);
        if (expiresAt != null) {
          await _tokenStorage.saveExpiresAt(expiresAt);
        }
      }
    }
  }

  dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    }

    String message = 'An unexpected server error occurred. Please try again.';
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map && decoded.containsKey('detail')) {
        message = decoded['detail'].toString();
      } else if (decoded is Map && decoded.containsKey('message')) {
        message = decoded['message'].toString();
      } else if (decoded is String) {
        message = decoded;
      }
    } catch (_) {
      if (response.statusCode == 404) {
        message = 'The requested resource was not found.';
      } else if (response.statusCode >= 500) {
        message = 'The server encountered an error. Please try again later.';
      } else if (response.statusCode == 401 || response.statusCode == 403) {
        message = 'You are not authorized to perform this action.';
      }
    }

    switch (response.statusCode) {
      case 400:
        throw ApiException(400, message);
      case 401:
        throw UnauthorizedException(message);
      case 403:
        throw ForbiddenException(message);
      case 404:
        throw NotFoundException(message);
      case 422:
        throw ValidationException(message);
      case 500:
        throw ServerException(message);
      default:
        throw ApiException(response.statusCode, message);
    }
  }

  Never _handleNetworkError(Object e) {
    if (e is ApiException) throw e;
    final errorString = e.toString().toLowerCase();
    if (errorString.contains('socket') || 
        errorString.contains('connection refused') || 
        errorString.contains('failed host lookup') ||
        errorString.contains('connection timed out')) {
      throw ApiException(503, 'Unable to connect to the server. Please check your internet connection or ensure the server is running.');
    }
    throw ApiException(500, 'An unexpected network error occurred. Please try again.');
  }
}
