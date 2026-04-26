class Prediction {
  final int? id;
  final String imagePath;
  final String predictedClass;
  final double confidenceScore;
  final DateTime timestamp;

  const Prediction({
    this.id,
    required this.imagePath,
    required this.predictedClass,
    required this.confidenceScore,
    required this.timestamp,
  });

  bool get isRusak => predictedClass.toLowerCase().contains('rusak');

  String get speciesName {
    return predictedClass.replaceAll(' Rusak', '').trim();
  }

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
