import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../core/api/api_client.dart';
import '../core/auth/auth_service.dart';
import '../core/auth/auth_state.dart';
import '../core/auth/token_storage.dart';
import '../features/admin/services/admin_service.dart';
import '../features/admin/providers/admin_state.dart';
import '../features/insurance/services/insurance_service.dart';
import '../features/insurance/providers/insurance_state.dart';
import '../features/mechanic/services/mechanic_service.dart';
import '../features/mechanic/providers/mechanic_state.dart';
import '../features/mechanic/services/records_service.dart';
import '../features/mechanic/providers/records_state.dart';
import '../features/owner/owner_state.dart';
import 'router.dart';
import 'package:google_fonts/google_fonts.dart';

class PapayGarageApp extends StatefulWidget {
  const PapayGarageApp({super.key});

  @override
  State<PapayGarageApp> createState() => _PapayGarageAppState();
}

class _PapayGarageAppState extends State<PapayGarageApp> {
  late final TokenStorage _tokenStorage;
  late final ApiClient _apiClient;
  late final AuthService _authService;
  late final AuthState _authState;
  
  late final AdminService _adminService;
  late final AdminState _adminState;

  late final InsuranceService _insuranceService;
  late final InsuranceState _insuranceState;

  late final MechanicService _mechanicService;
  late final MechanicState _mechanicState;

  late final RecordsService _recordsService;
  late final RecordsState _recordsState;

  late final OwnerState _ownerState;

  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    
    // Initialize foundation services
    _tokenStorage = TokenStorage();
    _apiClient = ApiClient(tokenStorage: _tokenStorage);
    _authService = AuthService(apiClient: _apiClient);
    _authState = AuthState(
      authService: _authService,
      tokenStorage: _tokenStorage,
    );
    
    // Initialize Admin services
    _adminService = AdminService(apiClient: _apiClient);
    _adminState = AdminState(adminService: _adminService);

    // Initialize Insurance services
    _insuranceService = InsuranceService(apiClient: _apiClient);
    _insuranceState = InsuranceState(service: _insuranceService);

    // Initialize Mechanic services
    _mechanicService = MechanicService(apiClient: _apiClient);
    _mechanicState = MechanicState(service: _mechanicService);

    _recordsService = RecordsService(apiClient: _apiClient);
    _recordsState = RecordsState(recordsService: _recordsService);

    // Initialize Owner state
    _ownerState = OwnerState(apiClient: _apiClient);

    _router = AppRouter.createRouter(_authState);

    // Bootstrap authentication state
    _authState.initialize();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: _authState),
        ChangeNotifierProvider.value(value: _adminState),
        ChangeNotifierProvider.value(value: _insuranceState),
        ChangeNotifierProvider.value(value: _mechanicState),
        ChangeNotifierProvider.value(value: _recordsState),
        ChangeNotifierProvider.value(value: _ownerState),
        Provider.value(value: _apiClient),
      ],
      child: MaterialApp.router(
        title: 'Papay Garage',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF1E88E5), // Papay Garage Theme Color
            brightness: Brightness.light,
          ),
          textTheme: GoogleFonts.interTextTheme(),
          useMaterial3: true,
          inputDecorationTheme: const InputDecorationTheme(
            filled: true,
            border: OutlineInputBorder(),
          ),
        ),
        routerConfig: _router,
      ),
    );
  }
}
