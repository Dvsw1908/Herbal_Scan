import 'dart:io';
import '../models/prediction.dart';
import '../services/api_service.dart';
import '../services/database_service.dart';

class PredictionRepository {
  final ApiService _api;
  final DatabaseService _db;

  PredictionRepository({ApiService? api, DatabaseService? db})
      : _api = api ?? ApiService(),
        _db = db ?? DatabaseService.instance;

  Future<Prediction> predict(File imageFile) async {
    final result = await _api.predict(imageFile);
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
