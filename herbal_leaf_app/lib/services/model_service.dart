import 'dart:io';
import 'dart:typed_data';
import 'package:pytorch_lite/pytorch_lite.dart';
import '../models/prediction.dart';

class ModelService {
  static const _modelAsset = 'assets/model/shufflenet_exp2.ptl';
  static const _labelAsset = 'assets/model/labels.txt';
  static const _imgSize    = 224;
  static const _numClasses = 32;
  static const _mean       = [0.5, 0.5, 0.5];
  static const _std        = [0.5, 0.5, 0.5];

  static const _classNames = [
    'Daun Alpukat BG',
    'Daun Alpukat NoBG',
    'Daun Alpukat Rusak BG',
    'Daun Alpukat Rusak NoBG',
    'Daun Belimbing Wuluh BG',
    'Daun Belimbing Wuluh NoBG',
    'Daun Belimbing Wuluh Rusak BG',
    'Daun Belimbing Wuluh Rusak NoBG',
    'Daun Jambu Biji Rusak BG',
    'Daun Jambu Biji Rusak NoBG',
    'Daun Jambu biji BG',
    'Daun Jambu biji NoBG',
    'Daun Leci BG',
    'Daun Leci NoBG',
    'Daun Leci Rusak BG',
    'Daun Leci Rusak NoBG',
    'Daun Nangka BG',
    'Daun Nangka NoBG',
    'Daun Nangka Rusak BG',
    'Daun Nangka Rusak NoBG',
    'Daun Salam BG',
    'Daun Salam NoBG',
    'Daun Salam Rusak BG',
    'Daun Salam Rusak NoBG',
    'Daun Sirsak BG',
    'Daun Sirsak NoBG',
    'Daun Sirsak Rusak BG',
    'Daun Sirsak Rusak NoBG',
    'Daun Srikaya BG',
    'Daun Srikaya NoBG',
    'Daun Srikaya Rusak BG',
    'Daun Srikaya Rusak NoBG',
  ];

  static final ModelService instance = ModelService._();
  ModelService._();

  ClassificationModel? _model;

  Future<void> init() async {
    if (_model != null) return;
    _model = await PytorchLite.loadClassificationModel(
      _modelAsset,
      _imgSize,
      _imgSize,
      _numClasses,
      labelPath: _labelAsset,
      ensureMatchingNumberOfClasses: false,
    );
  }

  Future<Prediction> predict(File imageFile) async {
    await init();

    final Uint8List bytes = await imageFile.readAsBytes();

    // Dapatkan probabilitas semua kelas (sudah di-softmax oleh pytorch_lite)
    final List<double> probs = await _model!.getImagePredictionListProbabilities(
      bytes,
      mean: _mean,
      std: _std,
    );

    // Top-3
    final indexed = List.generate(probs.length, (i) => MapEntry(i, probs[i]));
    indexed.sort((a, b) => b.value.compareTo(a.value));
    final top3 = indexed.take(3).map((e) => Top3Entry(
          className: _classNames[e.key],
          confidence: e.value,
        )).toList();

    return Prediction(
      imagePath: imageFile.path,
      predictedClass: top3.first.className,
      confidenceScore: top3.first.confidence,
      timestamp: DateTime.now(),
      top3: top3,
    );
  }
}
