import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_state.dart';

// ──────────────────────────────────────────────
// Design tokens 
// ──────────────────────────────────────────────
const _gold = Color(0xFFB8863A);
const _goldDark = Color(0xFF9C6F2C);
const _ink = Color(0xFF1C1812);
const _muted = Color(0xFF9A9080);
const _border = Color(0xFFE8E1D4);
const _bg = Color(0xFFEEE9DF);
const _cardBg = Color(0xFFFFFFFF);
const _inputBg = Color(0xFFFCFBF8);

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // Anything narrower than this is treated as "mobile" layout.
  static const double _mobileBreakpoint = 700;

  final _keyController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final FocusNode _focusNode = FocusNode();
  
  bool _isComplete = false;
  String? _statusMessage;
  bool _isError = false;

  @override
  void initState() {
    super.initState();
    _keyController.addListener(_onKeyChanged);
    _focusNode.addListener(() {
      setState(() {});
    });
  }

  void _onKeyChanged() {
    final text = _keyController.text.replaceAll('-', '');
    final isComplete = text.isNotEmpty;
    if (_isComplete != isComplete) {
      setState(() {
        _isComplete = isComplete;
      });
    }
    if (_statusMessage != null) {
      setState(() {
        _statusMessage = null;
        _isError = false;
      });
    }
  }

  @override
  void dispose() {
    _keyController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_isComplete) return;
    
    final authState = context.read<AuthState>();
    final success = await authState.login(_keyController.text.trim());
    
    // On success, AuthState becomes 'authenticated' and go_router
    // automatically redirects to the correct dashboard — no message needed.
    if (mounted && !success) {
      setState(() {
        _statusMessage = authState.errorMessage ?? 'This key isn\'t recognized. Double check it or contact your admin.';
        _isError = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = context.watch<AuthState>();
    final isLoading = authState.status == AuthStatus.authenticating;

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          // Background Gradient
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.topCenter,
                  radius: 1.2,
                  colors: [
                    _gold.withValues(alpha: 0.08),
                    Colors.transparent,
                  ],
                  stops: const [0.0, 0.55],
                ),
              ),
            ),
          ),
          LayoutBuilder(
            builder: (context, constraints) {
              final bool isMobile = constraints.maxWidth < _mobileBreakpoint;
              return Center(
                child: SingleChildScrollView(
                  padding: EdgeInsets.all(isMobile ? 16 : 24),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Container(
                      padding: EdgeInsets.fromLTRB(
                        isMobile ? 24 : 36,
                        isMobile ? 30 : 40,
                        isMobile ? 24 : 36,
                        isMobile ? 24 : 32,
                      ),
                      decoration: BoxDecoration(
                        color: _cardBg,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: _border),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x08211D16),
                            blurRadius: 40,
                            offset: Offset(0, 12),
                          ),
                        ],
                      ),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Glyph
                            Center(
                              child: Container(
                                width: 44,
                                height: 44,
                                margin: const EdgeInsets.only(bottom: 22),
                                decoration: BoxDecoration(
                                  color: _gold.withValues(alpha: 0.12),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.vpn_key_rounded,
                                  color: _goldDark,
                                  size: 22,
                                ),
                              ),
                            ),
                            // Title
                            Text(
                              'Activate your access',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: isMobile ? 19 : 22,
                                fontWeight: FontWeight.w800,
                                color: _ink,
                                letterSpacing: -0.5,
                              ),
                            ),
                            const SizedBox(height: 6),
                            // Subtitle
                            const Text(
                              'Enter the activation key provided by your admin to unlock your account.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 13.5,
                                height: 1.5,
                                color: _muted,
                              ),
                            ),
                            const SizedBox(height: 32),
                            // Field Label
                            const Text(
                              'ACTIVATION KEY',
                              style: TextStyle(
                                fontSize: 11.5,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.7,
                                color: _muted,
                              ),
                            ),
                            const SizedBox(height: 8),
                            // Input
                            TextFormField(
                              controller: _keyController,
                              focusNode: _focusNode,
                              enabled: !isLoading,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 1.8,
                                color: _ink,
                              ),
                              decoration: InputDecoration(
                                hintText: 'XXXXX-XXXXX-XXXXX-XXXXX',
                                hintStyle: TextStyle(
                                  color: _muted.withValues(alpha: 0.6),
                                  letterSpacing: 1.2,
                                ),
                                filled: true,
                                fillColor: _inputBg,
                                contentPadding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                  horizontal: 16,
                                ),
                                enabledBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10),
                                  borderSide: BorderSide(
                                    color: _isError ? const Color(0xFFD65C5A) : _border,
                                  ),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10),
                                  borderSide: BorderSide(
                                    color: _isError ? const Color(0xFFD65C5A) : _gold,
                                    width: 1.5,
                                  ),
                                ),
                                disabledBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10),
                                  borderSide: const BorderSide(
                                    color: _border,
                                  ),
                                ),
                              ),
                              onFieldSubmitted: (_) => _submit(),
                            ),
                            // Status Row
                            Container(
                              constraints: const BoxConstraints(minHeight: 18),
                              margin: const EdgeInsets.only(top: 10, bottom: 24, left: 2, right: 2),
                              child: _statusMessage != null
                                  ? Row(
                                      children: [
                                        Icon(
                                          _isError ? Icons.error_outline : Icons.check_circle_outline,
                                          size: 13,
                                          color: _isError ? const Color(0xFFD65C5A) : const Color(0xFF2F9366),
                                        ),
                                        const SizedBox(width: 6),
                                        Expanded(
                                          child: Text(
                                            _statusMessage!,
                                            style: TextStyle(
                                              fontSize: 12.5,
                                              fontWeight: FontWeight.w600,
                                              color: _isError ? const Color(0xFFD65C5A) : const Color(0xFF2F9366),
                                            ),
                                          ),
                                        ),
                                      ],
                                    )
                                  : null,
                            ),
                            // Button
                            ElevatedButton(
                              onPressed: (_isComplete && !isLoading) ? _submit : null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _gold,
                                disabledBackgroundColor: _gold.withValues(alpha: 0.45),
                                foregroundColor: Colors.white,
                                disabledForegroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 16),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                elevation: 0,
                              ).copyWith(
                                backgroundColor: WidgetStateProperty.resolveWith((states) {
                                  if (states.contains(WidgetState.disabled)) return _gold.withValues(alpha: 0.5);
                                  if (states.contains(WidgetState.hovered)) return _goldDark;
                                  return _gold;
                                }),
                              ),
                              child: isLoading
                                  ? const SizedBox(
                                      width: 16,
                                      height: 16,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : const Text(
                                      'Submit',
                                      style: TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 0.15,
                                      ),
                                    ),
                            ),
                            const SizedBox(height: 20),
                            // Footnote
                            const Text(
                              'Don\'t have a key? Contact your admin to request one.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                                color: _muted,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}