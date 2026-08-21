import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Colors matching the "Mechanic Workspace" mockup palette
class PlateColors {
  static const bg = Color(0xFFE7E9EC);
  static const ink = Color(0xFF1C1B1A);
  static const surface = Color(0xFFFFFFFF);
  static const surface2 = Color(0xFFF3F4F6);
  static const border = Color(0xFFDFE2E6);
  static const muted2 = Color(0xFF9CA3AF);
  static const accent = Color(0xFFE8592A);
  static const accentDark = Color(0xFFC6491F);
}

class PlateSearchBar extends StatefulWidget {
  final TextEditingController? controller;
  final double? width;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final String hintText;

  const PlateSearchBar({
    super.key,
    this.controller,
    this.width,
    this.onChanged,
    this.onSubmitted,
    this.hintText = 'ABC 1234',
  });

  @override
  State<PlateSearchBar> createState() => _PlateSearchBarState();
}

class _PlateSearchBarState extends State<PlateSearchBar> {
  // Use the caller's controller if one is passed in; otherwise fall back
  // to an internally-owned one so the widget still works standalone.
  late final TextEditingController _controller =
      widget.controller ?? TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _isFocused = false;
  bool _hasValue = false;

  @override
  void initState() {
    super.initState();
    _hasValue = _controller.text.isNotEmpty;
    _focusNode.addListener(() {
      setState(() => _isFocused = _focusNode.hasFocus);
    });
    _controller.addListener(() {
      setState(() => _hasValue = _controller.text.isNotEmpty);
      widget.onChanged?.call(_controller.text);
    });
  }

  @override
  void dispose() {
    // Only dispose the controller if we created it ourselves —
    // disposing a controller the caller owns would break their widget.
    if (widget.controller == null) {
      _controller.dispose();
    }
    _focusNode.dispose();
    super.dispose();
  }

  void _clear() {
    _controller.clear();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    // Mirrors the mockup's `.search input`: flat surface-2 fill, hairline
    // border, 8px radius, search icon inline at the left inset. On focus
    // the fill flips to white and the border becomes a 2px orange outline.
    final field = AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      curve: Curves.easeOut,
      decoration: BoxDecoration(
        color: _isFocused ? PlateColors.surface : PlateColors.surface2,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _isFocused ? PlateColors.accent : PlateColors.border,
          width: _isFocused ? 2 : 1,
        ),
      ),
      padding: EdgeInsets.symmetric(
        horizontal: _isFocused ? 13 : 14,
        vertical: _isFocused ? 10 : 11,
      ),
      child: Row(
        children: [
          Icon(Icons.search, size: 16, color: PlateColors.accentDark),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              onSubmitted: widget.onSubmitted,
              textCapitalization: TextCapitalization.characters,
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[A-Za-z0-9 ]')),
                UpperCaseTextFormatter(),
                LengthLimitingTextInputFormatter(10),
              ],
              style: const TextStyle(
                fontFamily: 'monospace',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                letterSpacing: 1,
                color: PlateColors.ink,
              ),
              decoration: InputDecoration(
                // Explicitly turned off — otherwise this TextField inherits
                // whatever `filled`/`fillColor` the app's global
                // InputDecorationTheme sets, which is what was producing
                // the grey box behind the text.
                filled: false,
                fillColor: Colors.transparent,
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                disabledBorder: InputBorder.none,
                isCollapsed: true,
                hintText: widget.hintText,
                hintStyle: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1,
                  color: PlateColors.muted2,
                ),
              ),
            ),
          ),
          if (_hasValue) ...[
            const SizedBox(width: 6),
            GestureDetector(
              onTap: _clear,
              child: Container(
                width: 20,
                height: 20,
                decoration: const BoxDecoration(
                  color: PlateColors.border,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.close,
                  size: 12,
                  color: PlateColors.ink,
                ),
              ),
            ),
          ],
        ],
      ),
    );

    // A fixed height keeps the bar visually level with the dashboard's
    // OutlinedButton/ElevatedButton (vertical:12 padding, ~44px tall).
    final sized = SizedBox(height: 44, width: widget.width, child: field);
    return widget.width != null ? sized : IntrinsicWidth(child: sized);
  }
}

/// Forces uppercase as the user types
class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    return TextEditingValue(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
  }
}

/// Example usage screen
class PlateSearchScreen extends StatelessWidget {
  const PlateSearchScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: PlateColors.bg,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: PlateSearchBar(
            onSubmitted: (value) {
              // Hook up real search logic here
              debugPrint('Searching for plate: $value');
            },
          ),
        ),
      ),
    );
  }
}