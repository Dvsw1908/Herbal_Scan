import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/prediction_provider.dart';
import 'pages/main_page.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const HerbalScanApp());
}

class HerbalScanApp extends StatelessWidget {
  const HerbalScanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) {
        final provider = PredictionProvider();
        Future.microtask(() => provider.init());
        return provider;
      },
      child: MaterialApp(
        title: 'HerbalScan',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorSchemeSeed: const Color(0xFF1F6F43),
          useMaterial3: true,
        ),
        home: const MainPage(),
      ),
    );
  }
}
