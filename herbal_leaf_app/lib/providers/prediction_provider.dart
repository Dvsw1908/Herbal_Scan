import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/prediction.dart';
import '../repositories/prediction_repository.dart';

enum PredictionState { idle, loading, success, error }

class PredictionProvider extends ChangeNotifier {
  final PredictionRepository _repo;

  PredictionProvider({PredictionRepository? repo})
      : _repo = repo ?? PredictionRepository();

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
      _lastResult = await _repo.predict(imageFile);
      _state = PredictionState.success;
      await loadHistory();
    } catch (e) {
      _errorMessage = e.toString();
      _state = PredictionState.error;
    }

    notifyListeners();
  }

  Future<void> init() => loadHistory();

  Future<void> loadHistory() async {
    _history = await _repo.getHistory();
    notifyListeners();
  }

  Future<void> deletePrediction(int id) async {
    await _repo.deletePrediction(id);
    _history = _history.where((p) => p.id != id).toList();
    notifyListeners();
  }

  Future<void> clearHistory() async {
    await _repo.clearHistory();
    _history = [];
    notifyListeners();
  }

  int _batchDone = 0;
  int _batchTotal = 0;
  int get batchDone => _batchDone;
  int get batchTotal => _batchTotal;

  Future<List<Prediction>> predictBatch(List<File> files) async {
    _state = PredictionState.loading;
    _batchDone = 0;
    _batchTotal = files.length;
    _errorMessage = null;
    notifyListeners();

    List<Prediction> results = [];
    try {
      results = await _repo.predictBatch(files, (done, total) {
        _batchDone = done;
        _batchTotal = total;
        notifyListeners();
      });
      _state = PredictionState.success;
      await loadHistory();
    } catch (e) {
      _errorMessage = e.toString();
      _state = PredictionState.error;
      notifyListeners();
    }
    return results;
  }

  void reset() {
    _state = PredictionState.idle;
    _lastResult = null;
    _errorMessage = null;
    notifyListeners();
  }
}
