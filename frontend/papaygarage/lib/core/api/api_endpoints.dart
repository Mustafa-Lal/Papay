class ApiEndpoints {
  // Use localhost for Windows desktop / Web. 
  // If running on Android emulator, this should be http://10.0.2.2:8000
  static const String baseUrl = 'http://localhost:5000';

  // Auth
  static const String activate = '/auth/activate';
  static const String logout = '/auth/logout';
  static const String me = '/auth/me';
  static const String versionCheck = '/auth/version-check';

  // Admin
  static const String adminAccessKeys = '/admin/access-keys';
  static const String adminSettingsVersion = '/admin/settings/version';

  // Insurance
  static const String insuranceInvoices = '/insurance/invoices';
  static const String insuranceCustomers = '/insurance/customers';
  static const String insuranceItems = '/insurance/items';
  static const String insuranceImages = '/insurance/images';
  // Mechanic Workspaces
  static const String mechanicInvoices = '/mechanic/invoices';
  static const String mechanicCustomers = '/mechanic/customers';
  static const String mechanicItems = '/mechanic/items';

  // Shared
  static const String products = '/products';
  static const String rent = '/rent';
  static const String utilityBills = '/utility-bills';
  static const String salaries = '/salaries';
  static const String expenses = '/expenses';
  static const String profits = '/profits';

  // Owner
  static const String summary = '/summary';
}
