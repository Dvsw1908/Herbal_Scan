import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import '../models/prediction.dart';

class CsvExportService {
  static Future<File> exportBatchPredictions({
    required List<Prediction> results,
    required String actualClass,
  }) async {
    final buffer = StringBuffer()
      ..writeln('No,Nama File,Kelas Daun,Prediksi Kelas Daun,Confidence Score');

    for (var i = 0; i < results.length; i++) {
      final prediction = results[i];
      final row = [
        '${i + 1}',
        p.basename(prediction.imagePath),
        actualClass,
        prediction.predictedClass,
        '${(prediction.confidenceScore * 100).toStringAsFixed(2)}%',
      ];
      buffer.writeln(row.map(_escapeCsv).join(','));
    }

    final directory =
        await getDownloadsDirectory() ??
        await getApplicationDocumentsDirectory();
    final timestamp = DateTime.now().toIso8601String().replaceAll(
      RegExp(r'[:.]'),
      '-',
    );
    final file = File(p.join(directory.path, 'hasil_prediksi_$timestamp.csv'));
    return file.writeAsString(buffer.toString(), flush: true);
  }

  static String _escapeCsv(String value) {
    if (!value.contains(RegExp(r'[",\n\r]'))) return value;
    return '"${value.replaceAll('"', '""')}"';
  }
}
