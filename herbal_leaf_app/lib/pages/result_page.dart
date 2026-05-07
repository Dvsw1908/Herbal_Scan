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
    final isUnrecognized = result.isUnrecognized;

    return Scaffold(
      backgroundColor: const Color(0xFFF0F7F4),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Hero image ────────────────────────────────────────────
            _HeroImage(imageFile: imageFile),

            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Header ──────────────────────────────────────────
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEAF3EC),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.auto_awesome_rounded,
                            color: Color(0xFFE8A020), size: 20),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Hasil Klasifikasi',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A1A2E),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // ── Tidak dikenali ───────────────────────────────────
                  if (isUnrecognized) ...[
                    _UnrecognizedCard(confidence: result.confidenceScore),
                    const SizedBox(height: 14),
                  ],

                  // ── Top result ────────────────────────────────────────
                  if (!isUnrecognized)
                    _ResultCard(
                      name: result.speciesName,
                      latinName: plant?.latinName ?? '',
                      confidence: result.confidenceScore,
                      isRusak: isRusak,
                      benefitSnippet: plant?.benefits.isNotEmpty == true
                          ? plant!.benefits.first
                          : null,
                    ),

                  // ── Daun rusak warning ─────────────────────────────
                  if (isRusak && !isUnrecognized) ...[
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: Colors.orange.shade100,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(Icons.warning_amber_rounded,
                                color: Colors.orange.shade700, size: 18),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Daun terdeteksi dalam kondisi rusak. '
                              'Hasil identifikasi mungkin kurang akurat.',
                              style: TextStyle(
                                  color: Colors.orange.shade800, fontSize: 13, height: 1.4),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],

                  // ── Top-3 predictions ──────────────────────────────
                  if (result.top3 != null && result.top3!.length > 1) ...[
                    const SizedBox(height: 24),
                    const Text(
                      'Prediksi Lainnya',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1A1A2E),
                      ),
                    ),
                    const SizedBox(height: 12),
                    _Top3Card(top3: result.top3!),
                  ],

                  const SizedBox(height: 28),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: () => Navigator.pop(context),
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF1F6F43),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16)),
                      ),
                      child: const Text(
                        'Selesai',
                        style: TextStyle(
                            fontSize: 15, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Hero image with gradient overlay + close button
// ─────────────────────────────────────────────────────────────────────────────
class _HeroImage extends StatelessWidget {
  final File imageFile;
  const _HeroImage({required this.imageFile});

  @override
  Widget build(BuildContext context) {
    final topPad = MediaQuery.of(context).padding.top;
    return SizedBox(
      width: double.infinity,
      height: 300 + topPad,
      child: Stack(
        children: [
          Positioned.fill(
            child: Image.file(
              imageFile,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                color: const Color(0xFF1B5E38),
                child: const Icon(Icons.broken_image_rounded,
                    color: Colors.white54, size: 64),
              ),
            ),
          ),
          // Dark gradient at top (for close button readability)
          Positioned(
            top: 0, left: 0, right: 0,
            child: Container(
              height: topPad + 80,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.black.withValues(alpha: 0.5), Colors.transparent],
                ),
              ),
            ),
          ),
          // Gradient overlay at bottom fading to background
          Positioned(
            bottom: 0, left: 0, right: 0,
            child: Container(
              height: 120,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Color(0xFFF0F7F4)],
                ),
              ),
            ),
          ),
          // Close button
          Positioned(
            top: topPad + 12,
            right: 16,
            child: GestureDetector(
              onTap: () => Navigator.pop(context),
              child: Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.45),
                  shape: BoxShape.circle,
                  border: Border.all(
                      color: Colors.white.withValues(alpha: 0.3), width: 1),
                ),
                child: const Icon(Icons.close_rounded,
                    color: Colors.white, size: 20),
              ),
            ),
          ),
          // "AI Scan" badge at bottom-left
          Positioned(
            bottom: 24, left: 20,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFF1F6F43),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.eco_rounded, color: Colors.white, size: 14),
                  SizedBox(width: 6),
                  Text(
                    'HerbalScan AI',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tidak dikenali card
// ─────────────────────────────────────────────────────────────────────────────
class _UnrecognizedCard extends StatelessWidget {
  final double confidence;
  const _UnrecognizedCard({required this.confidence});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.red.shade100,
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.help_outline_rounded,
                color: Colors.red.shade700, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Daun Tidak Dikenali',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Tingkat kepercayaan terlalu rendah '
                  '(${(confidence * 100).toStringAsFixed(1)}%). '
                  'Pastikan foto jelas, pencahayaan cukup, dan daun terlihat penuh.',
                  style: TextStyle(
                      color: Colors.red.shade800,
                      fontSize: 13,
                      height: 1.45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Top-1 result card
// ─────────────────────────────────────────────────────────────────────────────
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
    final color = isRusak ? const Color(0xFFE65100) : const Color(0xFF1F6F43);
    final gradientColors = isRusak
        ? [const Color(0xFFBF360C), const Color(0xFFE64A19)]
        : [const Color(0xFF1B5E38), const Color(0xFF2E9B61)];

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.14),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          // Gradient top banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: gradientColors,
              ),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(22)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.22),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.star_rounded,
                                color: Colors.white, size: 13),
                            SizedBox(width: 4),
                            Text(
                              'Paling Cocok',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          letterSpacing: -0.3,
                        ),
                      ),
                      if (latinName.isNotEmpty)
                        Text(
                          latinName,
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.75),
                            fontSize: 13,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: confidence),
                  duration: const Duration(milliseconds: 900),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, _) {
                    return Text(
                      '${(value * 100).toStringAsFixed(1)}%',
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        letterSpacing: -1,
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          // Confidence bar + benefit
          Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Tingkat Keyakinan',
                      style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                          fontWeight: FontWeight.w500),
                    ),
                    Text(
                      '${(confidence * 100).toStringAsFixed(1)}%',
                      style: TextStyle(
                          fontSize: 12,
                          color: color,
                          fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: confidence),
                  duration: const Duration(milliseconds: 1000),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, _) {
                    return LayoutBuilder(
                      builder: (_, constraints) => Stack(
                        children: [
                          Container(
                            height: 8,
                            width: constraints.maxWidth,
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                          Container(
                            height: 8,
                            width: constraints.maxWidth * value.clamp(0.0, 1.0),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(4),
                              gradient: LinearGradient(
                                colors: gradientColors,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),

                if (benefitSnippet != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.06),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.local_florist_rounded,
                            color: color, size: 16),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            benefitSnippet!,
                            style: TextStyle(
                                color: color, fontSize: 13, height: 1.4),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Top-3 list card
// ─────────────────────────────────────────────────────────────────────────────
class _Top3Card extends StatelessWidget {
  final List<Top3Entry> top3;
  const _Top3Card({required this.top3});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: top3.asMap().entries.map((entry) {
          final rank = entry.key + 1;
          final item = entry.value;
          final isFirst = rank == 1;
          final color = isFirst
              ? const Color(0xFF1F6F43)
              : Colors.grey.shade400;

          return Padding(
            padding: EdgeInsets.only(bottom: rank < top3.length ? 16 : 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 26,
                      height: 26,
                      decoration: BoxDecoration(
                        color: isFirst
                            ? const Color(0xFF1F6F43)
                            : Colors.grey.shade100,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          '$rank',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: isFirst ? Colors.white : Colors.grey.shade500,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        item.className,
                        style: TextStyle(
                          fontWeight: isFirst ? FontWeight.bold : FontWeight.normal,
                          fontSize: 14,
                          color: const Color(0xFF1A1A2E),
                        ),
                      ),
                    ),
                    Text(
                      item.percent,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: color,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: item.confidence),
                  duration: Duration(milliseconds: 800 + rank * 100),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, _) {
                    return LayoutBuilder(
                      builder: (_, constraints) => Stack(
                        children: [
                          Container(
                            height: 6,
                            width: constraints.maxWidth,
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                          Container(
                            height: 6,
                            width: constraints.maxWidth * value.clamp(0.0, 1.0),
                            decoration: BoxDecoration(
                              color: color,
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}
