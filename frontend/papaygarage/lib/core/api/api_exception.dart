class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException: [$statusCode] $message';
}

class UnauthorizedException extends ApiException {
  UnauthorizedException(String message) : super(401, message);
}

class ForbiddenException extends ApiException {
  ForbiddenException(String message) : super(403, message);
}

class NotFoundException extends ApiException {
  NotFoundException(String message) : super(404, message);
}

class ValidationException extends ApiException {
  ValidationException(String message) : super(422, message);
}

class ServerException extends ApiException {
  ServerException(String message) : super(500, message);
}
