import 'dart:io';
import '../models/prediction.dart';
import '../services/model_service.dart';
import '../services/database_service.dart';

class PredictionRepository {
  final DatabaseService _db;

  PredictionRepository({DatabaseService? db})
      : _db = db ?? DatabaseService.instance;

  Future<Prediction> predict(File imageFile) async {
    final result = await ModelService.instance.predict(imageFile);
    final id = await _db.insertPrediction(result);
    return Prediction(
      id: id,
      imagePath: result.imagePath,
      predictedClass: result.predictedClass,
      confidenceScore: result.confidenceScore,
      timestamp: result.timestamp,
      top3: result.top3,
    );
  }

  Future<List<Prediction>> getHistory() => _db.getAllPredictions();

  Future<void> deletePrediction(int id) => _db.deletePrediction(id);

  Future<void> clearHistory() => _db.clearAll();
}
