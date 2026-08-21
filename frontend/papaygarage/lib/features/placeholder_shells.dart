import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_state.dart';

class AdminShellScreen extends StatelessWidget {
  const AdminShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Papay Garage - Admin'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthState>().logout(),
          ),
        ],
      ),
      body: const Center(
        child: Text('Welcome Admin! Workspace Placeholder.'),
      ),
    );
  }
}

class InsuranceShellScreen extends StatelessWidget {
  const InsuranceShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Papay Garage - Insurance'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthState>().logout(),
          ),
        ],
      ),
      body: const Center(
        child: Text('Welcome Insurance! Workspace Placeholder.'),
      ),
    );
  }
}

class MechanicShellScreen extends StatelessWidget {
  const MechanicShellScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Papay Garage - Mechanic'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthState>().logout(),
          ),
        ],
      ),
      body: const Center(
        child: Text('Welcome Mechanic! Workspace Placeholder.'),
      ),
    );
  }
}
