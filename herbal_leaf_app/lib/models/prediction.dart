class Top3Entry {
  final String className;
  final double confidence;

  const Top3Entry({required this.className, required this.confidence});

  factory Top3Entry.fromJson(Map<String, dynamic> json) => Top3Entry(
        className: json['class'] as String,
        confidence: (json['confidence'] as num).toDouble(),
      );

  String get percent => '${(confidence * 100).toStringAsFixed(1)}%';
}

class Prediction {
  final int? id;
  final String imagePath;
  final String predictedClass;
  final double confidenceScore;
  final DateTime timestamp;
  final List<Top3Entry>? top3;

  const Prediction({
    this.id,
    required this.imagePath,
    required this.predictedClass,
    required this.confidenceScore,
    required this.timestamp,
    this.top3,
  });

  bool get isRusak => predictedClass.toLowerCase().contains('rusak');

  bool get isUnrecognized => confidenceScore < 0.70;

  String get speciesName => predictedClass
      .replaceAll(RegExp(r'\s+Rusak', caseSensitive: false), '')
      .replaceAll(RegExp(r'\s+(NoBG|BG)\s*$', caseSensitive: false), '')
      .trim();

  String get confidencePercent =>
      '${(confidenceScore * 100).toStringAsFixed(1)}%';

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      id: json['id'] as int?,
      imagePath: json['image_path'] as String? ?? json['imagePath'] as String,
      predictedClass: json['predicted_class'] as String? ??
          json['predictedClass'] as String,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ??
          (json['confidenceScore'] as num).toDouble(),
      timestamp: json['timestamp'] is String
          ? DateTime.parse(json['timestamp'] as String)
          : json['timestamp'] as DateTime,
      top3: json['top3'] != null
          ? (json['top3'] as List<dynamic>)
              .map((e) => Top3Entry.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'image_path': imagePath,
      'predicted_class': predictedClass,
      'confidence_score': confidenceScore,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
