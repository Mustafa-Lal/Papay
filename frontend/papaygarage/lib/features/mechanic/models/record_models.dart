class RecordCategory {
  final String id;
  final String label;
  final String icon; // IconData as String or we'll just map it in the UI
  final int color;
  final int softColor;
  final List<RecordColumn> columns;

  const RecordCategory({
    required this.id,
    required this.label,
    required this.icon,
    required this.color,
    required this.softColor,
    required this.columns,
  });
}

class RecordColumn {
  final String key;
  final String label;
  final String type; // 'text', 'number', 'select'
  final double flex;
  final String placeholder;
  final List<String>? options;

  const RecordColumn({
    required this.key,
    required this.label,
    required this.type,
    required this.flex,
    required this.placeholder,
    this.options,
  });
}
