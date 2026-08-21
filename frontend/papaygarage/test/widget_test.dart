import 'package:flutter_test/flutter_test.dart';
import 'package:papaygarage/app/app.dart';

void main() {
  testWidgets('App starts without crashing', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const PapayGarageApp());

    // Basic smoke test - check if Papay Garage text is on screen (from login screen)
    expect(find.text('PAPAY GARAGE'), findsOneWidget);
  });
}
