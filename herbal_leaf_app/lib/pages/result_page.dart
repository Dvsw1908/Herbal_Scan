import 'dart:io';
import 'package:flutter/material.dart';
import '../models/prediction.dart';
import '../data/plant_data.dart';

class ResultPage extends StatelessWidget {
  final Prediction result;
  final File imageFile;

  const ResultPage({
    super.key,
    required this.result,
    required this.imageFile,
  });

  @override
  Widget build(BuildContext context) {
    final plant = findPlant(result.speciesName);
    final isRusak = result.isRusak;
    final confidence = result.confidenceScore;

    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F3),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Image with close button
              Stack(
                children: [
                  SizedBox(
                    width: double.infinity,
                    height: 280,
                    child: Image.file(imageFile, fit: BoxFit.cover),
                  ),
                  Positioned(
                    top: 12,
                    right: 12,
                    child: GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        width: 36,
                        height: 36,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.close, size: 20),
                      ),
                    ),
                  ),
                ],
              ),

              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome,
                            color: Color(0xFFE8A020), size: 22),
                        const SizedBox(width: 8),
                        Text(
                          'Hasil Klasifikasi',
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Top result card
                    _ResultCard(
                      name: result.speciesName,
                      latinName: plant?.latinName ?? '',
                      confidence: confidence,
                      isRusak: isRusak,
                      benefitSnippet: plant?.benefits.isNotEmpty == true
                          ? plant!.benefits.first
                          : null,
                    ),

                    if (isRusak) ...[
                      const SizedBox(height: 12),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.orange.shade200),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.warning_amber_rounded,
                                color: Colors.orange.shade700, size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Daun terdeteksi dalam kondisi rusak. '
                                'Hasil identifikasi mungkin kurang akurat.',
                                style: TextStyle(
                                    color: Colors.orange.shade800, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: () => Navigator.pop(context),
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF1F6F43),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12)),
                        ),
                        child: const Text('Selesai'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final String name;
  final String latinName;
  final double confidence;
  final bool isRusak;
  final String? benefitSnippet;

  const _ResultCard({
    required this.name,
    required this.latinName,
    required this.confidence,
    required this.isRusak,
    this.benefitSnippet,
  });

  @override
  Widget build(BuildContext context) {
    final color =
        isRusak ? Colors.orange.shade700 : const Color(0xFF1F6F43);
    final badgeColor = isRusak ? Colors.orange : const Color(0xFF1F6F43);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // "Paling Cocok" badge
          Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding:
                const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: badgeColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.star, color: Colors.white, size: 13),
                const SizedBox(width: 4),
                const Text(
                  'Paling Cocok',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),

          // Name + confidence
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(
                          fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    if (latinName.isNotEmpty)
                      Text(
                        latinName,
                        style: const TextStyle(
                            fontSize: 13,
                            fontStyle: FontStyle.italic,
                            color: Colors.black54),
                      ),
                  ],
                ),
              ),
              Text(
                '${(confidence * 100).toStringAsFixed(1)}%',
                style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: color),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Confidence bar
          LayoutBuilder(
            builder: (_, constraints) => Stack(
              children: [
                Container(
                  height: 8,
                  width: constraints.maxWidth,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                Container(
                  height: 8,
                  width: constraints.maxWidth * confidence.clamp(0.0, 1.0),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(4),
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1F6F43), Color(0xFFF5A623)],
                    ),
                  ),
                ),
              ],
            ),
          ),

          if (benefitSnippet != null) ...[
            const SizedBox(height: 12),
            RichText(
              text: TextSpan(
                children: [
                  const TextSpan(
                    text: 'Manfaat: ',
                    style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFE8A020),
                        fontSize: 14),
                  ),
                  TextSpan(
                    text: benefitSnippet,
                    style: const TextStyle(
                        color: Color(0xFFE8A020), fontSize: 14),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
