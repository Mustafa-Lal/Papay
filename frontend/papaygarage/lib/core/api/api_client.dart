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
    
    final response = await _client.get(uri, headers: headers);
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
  }

  /// Perform a POST request
  Future<dynamic> post(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    final response = await _client.post(
      uri,
      headers: headers,
      body: body != null ? jsonEncode(body) : null,
    );
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
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
    
    // http.MultipartRequest doesn't automatically merge standard headers perfectly if Content-Type is overridden,
    // but we can pass our custom Auth headers safely.
    final request = http.MultipartRequest('POST', uri);
    
    // We remove Content-Type because MultipartRequest needs to set its own Content-Type with the boundary.
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

    final streamedResponse = await _client.send(request);
    final response = await http.Response.fromStream(streamedResponse);
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
  }

  /// Perform a PUT request
  Future<dynamic> put(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    final response = await _client.put(
      uri,
      headers: headers,
      body: body != null ? jsonEncode(body) : null,
    );
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
  }

  /// Perform a PATCH request
  Future<dynamic> patch(String endpoint, {dynamic body}) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    final response = await _client.patch(
      uri,
      headers: headers,
      body: body != null ? jsonEncode(body) : null,
    );
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
  }

  /// Perform a DELETE request
  Future<dynamic> delete(String endpoint) async {
    final uri = _buildUri(endpoint);
    final headers = await buildHeaders();
    
    final response = await _client.delete(uri, headers: headers);
    await _handleSessionRefresh(response);
    
    return _processResponse(response);
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

  /// Extracts the new token from the response headers if the session was renewed
  Future<void> _handleSessionRefresh(http.Response response) async {
    final newToken = response.headers['x-session-token'];
    if (newToken != null && newToken.isNotEmpty) {
      await _tokenStorage.saveToken(newToken);
    }
  }

  dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    }

    String message = 'Unknown error occurred.';
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map && decoded.containsKey('detail')) {
        message = decoded['detail'].toString();
      } else {
        message = response.body;
      }
    } catch (_) {
      message = response.body.isNotEmpty ? response.body : response.reasonPhrase ?? 'Error';
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
}
