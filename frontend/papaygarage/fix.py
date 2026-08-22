import os
import re

files_to_fix = [
    "lib/core/api/api_client.dart",
    "lib/core/auth/auth_service.dart",
    "lib/core/auth/auth_state.dart",
    "lib/features/admin/models/access_key_model.dart",
    "lib/features/admin/providers/admin_state.dart",
    "lib/features/admin/screens/create_key_dialog.dart",
    "lib/features/admin/services/admin_service.dart",
    "lib/features/admin/widgets/status_badge.dart",
    "lib/features/auth/screens/login_screen.dart",
    "lib/features/insurance/providers/insurance_state.dart",
    "lib/features/insurance/screens/create_invoice_screen.dart",
    "lib/features/insurance/screens/edit_invoice_screen.dart",
    "lib/features/insurance/screens/insurance_dashboard_screen.dart",
    "lib/features/insurance/screens/invoice_detail_screen.dart",
    "lib/features/insurance/services/insurance_service.dart",
    "lib/features/mechanic/providers/mechanic_state.dart",
    "lib/features/mechanic/providers/records_state.dart",
    "lib/features/mechanic/screens/create_mechanic_invoice_screen.dart",
    "lib/features/mechanic/screens/edit_invoice_screen.dart",
    "lib/features/mechanic/screens/garage_records_screen.dart",
    "lib/features/mechanic/screens/mechanic_dashboard_screen.dart",
    "lib/features/mechanic/screens/mechanic_invoice_detail_screen.dart",
    "lib/features/mechanic/services/mechanic_service.dart",
    "lib/features/mechanic/services/records_service.dart",
    "lib/features/owner/owner_dashboard_screen.dart",
]

for file in files_to_fix:
    path = os.path.join(r"C:\Users\LEGION\papay-garage\frontend\papaygarage", file.replace('/', '\\'))
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix .withOpacity(x) -> .withValues(alpha: x)
    content = re.sub(r'\.withOpacity\((.*?)\)', r'.withValues(alpha: \1)', content)
    
    # Fix prefer_initializing_formals (e.g. required TokenStorage tokenStorage) : _tokenStorage = tokenStorage -> required this._tokenStorage
    # This might be tricky with regex, we can do some specific replacements
    content = re.sub(r'required TokenStorage tokenStorage(,?)\s*\}:\s*_tokenStorage\s*=\s*tokenStorage,?', r'required this._tokenStorage\1 :', content)
    content = re.sub(r'required ApiClient apiClient(,?)\s*\}:\s*_apiClient\s*=\s*apiClient,?', r'required this._apiClient\1 :', content)
    content = re.sub(r'required AuthService authService(,?)\s*\}:\s*_authService\s*=\s*authService,?', r'required this._authService\1 :', content)
    content = re.sub(r'required AdminService adminService(,?)\s*\}:\s*_adminService\s*=\s*adminService,?', r'required this._adminService\1 :', content)
    content = re.sub(r'required InsuranceService service(,?)\s*\}:\s*_service\s*=\s*service,?', r'required this._service\1 :', content)
    content = re.sub(r'required MechanicService service(,?)\s*\}:\s*_service\s*=\s*service,?', r'required this._service\1 :', content)
    content = re.sub(r'required RecordsService recordsService(,?)\s*\}:\s*_recordsService\s*=\s*recordsService,?', r'required this._recordsService\1 :', content)
    
    # Fix initialValue in create_key_dialog
    if "create_key_dialog.dart" in file:
        content = content.replace("value: ", "initialValue: ")
    
    # Unnecessary imports
    if "login_screen.dart" in file:
        content = re.sub(r"import 'package:flutter/services\.dart';\n?", "", content)
    if "insurance_dashboard_screen.dart" in file:
        content = re.sub(r"import '\.\./providers/insurance_state\.dart';\n?", "", content)
    if "mechanic_dashboard_screen.dart" in file:
        content = re.sub(r"import '\.\./providers/mechanic_state\.dart';\n?", "", content)

    # _goldSoft / _gold unused elements
    content = re.sub(r"const Color _goldSoft.*?;", "", content)
    content = re.sub(r"const Color _gold\s*=.*?;", "", content)

    # toList in spreads
    content = content.replace("...parts.map((p) => p.toJson()).toList(),", "...parts.map((p) => p.toJson()),")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done basic fixes.")
