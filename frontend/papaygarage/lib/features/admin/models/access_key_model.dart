class AccessKeyModel {
  final int id;
  final int roleId;
  final String roleName;
  final bool active;
  final DateTime createdAt;

  AccessKeyModel({
    required this.id,
    required this.roleId,
    required this.roleName,
    required this.active,
    required this.createdAt,
  });

  factory AccessKeyModel.fromJson(Map<String, dynamic> json) {
    final rId = json['role_id'] as int;
    // Map roleId to string locally since the backend only returns role_id
    String rName = 'Unknown';
    if (rId == 1) rName = 'INSURANCE';
    else if (rId == 2) rName = 'MECHANIC';
    else if (rId == 3) rName = 'OWNER';
    else if (rId == 4) rName = 'ADMIN';

    return AccessKeyModel(
      id: json['id'] as int,
      roleId: rId,
      roleName: rName,
      active: json['active'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class AccessKeyCreateResponse {
  final int id;
  final String roleName;
  final String rawKey;

  AccessKeyCreateResponse({
    required this.id,
    required this.roleName,
    required this.rawKey,
  });

  factory AccessKeyCreateResponse.fromJson(Map<String, dynamic> json) {
    return AccessKeyCreateResponse(
      id: json['access_key_id'] as int,
      roleName: json['role'] as String,
      rawKey: json['key'] as String,
    );
  }
}
