import 'package:flutter/material.dart';
import '../models/access_key_model.dart';
import '../services/admin_service.dart';
import '../../../core/api/api_exception.dart';

class AdminState extends ChangeNotifier {
  final AdminService _adminService;

  List<AccessKeyModel> _keys = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<AccessKeyModel> get keys => _keys;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  AdminState({required AdminService adminService}) : _adminService = adminService;

  Future<void> fetchKeys() async {
    _setLoading(true);
    try {
      _keys = await _adminService.getAccessKeys();
    } on ApiException catch (e) {
      _setError(e.message);
    } catch (e) {
      _setError('Failed to fetch access keys.');
    } finally {
      _setLoading(false);
    }
  }

  Future<AccessKeyCreateResponse?> createKey(int roleId) async {
    _setLoading(true);
    try {
      final response = await _adminService.createAccessKey(roleId);
      
      // Optimistic update instead of fetchKeys()
      final newKey = AccessKeyModel(
        id: response.id,
        roleId: roleId,
        roleName: response.roleName,
        active: false,
        createdAt: DateTime.now(),
      );
      _keys.add(newKey);
      _setLoading(false);
      
      return response;
    } on ApiException catch (e) {
      _setError(e.message);
      _setLoading(false);
      return null;
    } catch (e) {
      _setError('Failed to create access key.');
      _setLoading(false);
      return null;
    }
  }

  Future<void> toggleKeyStatus(int keyId, bool currentStatus) async {
    // Optimistic UI update
    final index = _keys.indexWhere((k) => k.id == keyId);
    if (index != -1) {
      final oldKey = _keys[index];
      _keys[index] = AccessKeyModel(
        id: oldKey.id,
        roleId: oldKey.roleId,
        roleName: oldKey.roleName,
        active: !currentStatus,
        createdAt: oldKey.createdAt,
      );
      notifyListeners();
    }

    try {
      if (currentStatus) {
        await _adminService.deactivateKey(keyId);
      } else {
        await _adminService.activateKey(keyId);
      }
    } catch (e) {
      // Revert on failure
      if (index != -1) {
        final oldKey = _keys[index];
        _keys[index] = AccessKeyModel(
          id: oldKey.id,
          roleId: oldKey.roleId,
          roleName: oldKey.roleName,
          active: currentStatus,
          createdAt: oldKey.createdAt,
        );
      }
      _setError(e is ApiException ? e.message : 'Failed to update key status.');
    }
  }

  Future<void> deleteKey(int keyId) async {
    // Optimistic UI update
    final index = _keys.indexWhere((k) => k.id == keyId);
    AccessKeyModel? oldKey;
    if (index != -1) {
      oldKey = _keys[index];
      _keys.removeAt(index);
      notifyListeners();
    }

    try {
      await _adminService.deleteKey(keyId);
    } catch (e) {
      // Revert on failure
      if (oldKey != null) {
        _keys.insert(index, oldKey);
        notifyListeners();
      }
      _setError(e is ApiException ? e.message : 'Failed to delete access key.');
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    if (loading) {
      _errorMessage = null;
    }
    notifyListeners();
  }

  void _setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  void clearError() {
    if (_errorMessage != null) {
      _errorMessage = null;
      notifyListeners();
    }
  }
}
