import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/prediction.dart';

class ApiService {
  // Ganti BASE_URL dengan IP server backend saat testing di device fisik
  // Contoh: 'http://192.168.1.10:8000'
  static const String baseUrl = 'http://10.0.2.2:8000';

  static const Duration _timeout = Duration(seconds: 30);

  /// Upload gambar ke backend dan kembalikan hasil prediksi
  Future<Prediction> predict(File imageFile) async {
    final uri = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', uri);

    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );

    final streamedResponse = await request.send().timeout(_timeout);
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return Prediction(
        id: json['id'] as int?,
        imagePath: imageFile.path,
        predictedClass: json['predicted_class'] as String,
        confidenceScore: (json['confidence_score'] as num).toDouble(),
        timestamp: DateTime.now(),
      );
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    throw ApiException(
      statusCode: response.statusCode,
      message: body['detail'] as String? ?? 'Terjadi kesalahan pada server.',
    );
  }

  /// Ambil riwayat dari backend (opsional, history diambil dari lokal)
  Future<List<Prediction>> fetchHistory() async {
    final uri = Uri.parse('$baseUrl/history');
    final response = await http.get(uri).timeout(_timeout);

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>;
      return list
          .map((e) => Prediction.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: 'Gagal mengambil riwayat dari server.',
    );
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  const ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
