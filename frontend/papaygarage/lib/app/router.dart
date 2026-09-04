import 'package:go_router/go_router.dart';
import '../core/auth/auth_state.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/update_screen.dart';
import '../features/admin/screens/admin_dashboard_screen.dart';
import '../features/insurance/screens/insurance_dashboard_screen.dart';
import '../features/mechanic/screens/mechanic_dashboard_screen.dart';
import '../features/owner/owner_dashboard_screen.dart';

class AppRouter {
  static GoRouter createRouter(AuthState authState) {
    return GoRouter(
      initialLocation: '/login',
      refreshListenable: authState,
      redirect: (context, state) {
        final authStatus = authState.status;
        final isLoggingIn = state.matchedLocation == '/login';

        // Wait until initialization finishes
        if (authStatus == AuthStatus.initial) {
          return null; // Let the splash/loading screen show
        }

        // Update required flow
        if (authStatus == AuthStatus.updateRequired && state.matchedLocation != '/update') {
          return '/update';
        }

        // Unauthenticated users must go to login
        if (authStatus == AuthStatus.unauthenticated && !isLoggingIn) {
          return '/login';
        }

        // Authenticated users should not be on the login screen
        if (authStatus == AuthStatus.authenticated && isLoggingIn) {
          final role = authState.role;
          if (role == 'ADMIN')     return '/admin';
          if (role == 'INSURANCE') return '/insurance';
          if (role == 'MECHANIC')  return '/mechanic';
          if (role == 'OWNER')     return '/owner';
          return '/login'; // Fallback if role is unknown
        }

        return null; // No redirection needed
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/update',
          builder: (context, state) => const UpdateScreen(),
        ),
        GoRoute(
          path: '/admin',
          builder: (context, state) => const AdminDashboardScreen(),
        ),
        GoRoute(
          path: '/insurance',
          builder: (context, state) => const InsuranceDashboardScreen(),
        ),
        GoRoute(
          path: '/mechanic',
          builder: (context, state) => const MechanicDashboardScreen(),
        ),
        GoRoute(
          path: '/owner',
          builder: (context, state) => const OwnerDashboardScreen(),
        ),
      ],
    );
  }
}
