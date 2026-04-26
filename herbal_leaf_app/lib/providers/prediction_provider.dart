import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/prediction.dart';
import '../services/api_service.dart';
import '../services/database_service.dart';

enum PredictionState { idle, loading, success, error }

class PredictionProvider extends ChangeNotifier {
  final _api = ApiService();
  final _db = DatabaseService.instance;

  PredictionState _state = PredictionState.idle;
  Prediction? _lastResult;
  String? _errorMessage;
  List<Prediction> _history = [];

  PredictionState get state => _state;
  Prediction? get lastResult => _lastResult;
  String? get errorMessage => _errorMessage;
  List<Prediction> get history => List.unmodifiable(_history);

  Future<void> predictImage(File imageFile) async {
    _state = PredictionState.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _api.predict(imageFile);
      await _db.insertPrediction(result);
      _lastResult = result;
      _state = PredictionState.success;
      await loadHistory();
    } on ApiException catch (e) {
      _errorMessage = e.message;
      _state = PredictionState.error;
    } catch (e) {
      _errorMessage =
          'Tidak dapat terhubung ke server. Pastikan backend berjalan.';
      _state = PredictionState.error;
    }

    notifyListeners();
  }

  Future<void> init() async {
    await loadHistory();
  }

  Future<void> loadHistory() async {
    _history = await _db.getAllPredictions();
    notifyListeners();
  }

  Future<void> deletePrediction(int id) async {
    await _db.deletePrediction(id);
    _history = _history.where((p) => p.id != id).toList();
    notifyListeners();
  }

  Future<void> clearHistory() async {
    await _db.clearAll();
    _history = [];
    notifyListeners();
  }

  void reset() {
    _state = PredictionState.idle;
    _lastResult = null;
    _errorMessage = null;
    notifyListeners();
  }
}
