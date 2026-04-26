import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:herbal_leaf_app/main.dart';

void main() {
  testWidgets('HerbalScanApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const HerbalScanApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
