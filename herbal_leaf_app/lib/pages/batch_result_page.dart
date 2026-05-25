import 'dart:io';
import 'package:flutter/material.dart';
import '../models/prediction.dart';
import 'result_page.dart';

class BatchResultPage extends StatelessWidget {
  final List<Prediction> results;

  const BatchResultPage({super.key, required this.results});

  // Group by speciesName, count & average confidence
  List<_SpeciesStat> _buildSpeciesStats() {
    final Map<String, List<double>> map = {};
    for (final p in results) {
      final key = p.isUnrecognized ? 'Tidak Dikenali' : p.speciesName;
      map.putIfAbsent(key, () => []).add(p.confidenceScore);
    }
    return map.entries
        .map((e) => _SpeciesStat(
              name: e.key,
              count: e.value.length,
              avgConfidence:
                  e.value.reduce((a, b) => a + b) / e.value.length,
            ))
        .toList()
      ..sort((a, b) => b.count.compareTo(a.count));
  }

  @override
  Widget build(BuildContext context) {
    final total = results.length;
    final rusak = results.where((p) => p.isRusak).length;
    final unrecognized = results.where((p) => p.isUnrecognized).length;
    final ok = total - rusak - unrecognized;
    final speciesStats = _buildSpeciesStats();

    return Scaffold(
      backgroundColor: const Color(0xFFF0F7F4),
      body: CustomScrollView(
        slivers: [
          _buildAppBar(context),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: _SummaryRow(
                  total: total, ok: ok, rusak: rusak, unrecognized: unrecognized),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
              child: _SpeciesBreakdown(stats: speciesStats, total: total),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text(
                'Detail per Gambar',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: const Color(0xFF1A1A2E)),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, i) => _ResultTile(
                  index: i + 1,
                  prediction: results[i],
                ),
                childCount: results.length,
              ),
            ),
          ),
        ],
      ),
    );
  }

  SliverAppBar _buildAppBar(BuildContext context) {
    return SliverAppBar(
      pinned: true,
      backgroundColor: const Color(0xFF1B5E38),
      foregroundColor: Colors.white,
      title: Text(
        'Hasil Batch (${results.length} foto)',
        style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
      ),
      actions: [
        TextButton.icon(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.check_rounded, color: Colors.white, size: 18),
          label: const Text('Selesai',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final int total, ok, rusak, unrecognized;
  const _SummaryRow(
      {required this.total,
      required this.ok,
      required this.rusak,
      required this.unrecognized});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 12,
              offset: const Offset(0, 4)),
        ],
      ),
      child: Row(
        children: [
          _SummaryChip(label: 'Total', value: '$total', color: const Color(0xFF1565C0)),
          const SizedBox(width: 10),
          _SummaryChip(label: 'Terdeteksi', value: '$ok', color: const Color(0xFF1F6F43)),
          const SizedBox(width: 10),
          _SummaryChip(label: 'Rusak', value: '$rusak', color: Colors.orange.shade700),
          const SizedBox(width: 10),
          _SummaryChip(
              label: 'Tak Dikenal', value: '$unrecognized', color: Colors.red.shade600),
        ],
      ),
    );
  }
}

class _SummaryChip extends StatelessWidget {
  final String label, value;
  final Color color;
  const _SummaryChip(
      {required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          children: [
            Text(value,
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: color)),
            const SizedBox(height: 2),
            Text(label,
                style: TextStyle(
                    fontSize: 10,
                    color: color.withValues(alpha: 0.8),
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _ResultTile extends StatelessWidget {
  final int index;
  final Prediction prediction;
  const _ResultTile({required this.index, required this.prediction});

  @override
  Widget build(BuildContext context) {
    final isRusak = prediction.isRusak;
    final isUnrecognized = prediction.isUnrecognized;
    final Color statusColor = isUnrecognized
        ? Colors.red.shade600
        : isRusak
            ? Colors.orange.shade700
            : const Color(0xFF1F6F43);
    final String statusLabel = isUnrecognized
        ? 'Tak Dikenal'
        : isRusak
            ? 'Rusak'
            : 'Normal';
    final IconData statusIcon = isUnrecognized
        ? Icons.help_outline_rounded
        : isRusak
            ? Icons.warning_amber_rounded
            : Icons.check_circle_rounded;

    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResultPage(
            result: prediction,
            imageFile: File(prediction.imagePath),
          ),
        ),
      ),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 3)),
          ],
        ),
        child: Row(
          children: [
            // Thumbnail
            ClipRRect(
              borderRadius: const BorderRadius.horizontal(left: Radius.circular(18)),
              child: SizedBox(
                width: 82,
                height: 82,
                child: Image.file(
                  File(prediction.imagePath),
                  fit: BoxFit.cover,
                  errorBuilder: (_, _, _) => Container(
                    color: Colors.grey.shade200,
                    child: const Icon(Icons.broken_image_rounded,
                        color: Colors.grey, size: 32),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 14),
            // Info
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 7, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1565C0).withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text('$index',
                              style: const TextStyle(
                                  fontSize: 11,
                                  color: Color(0xFF1565C0),
                                  fontWeight: FontWeight.bold)),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 7, vertical: 2),
                          decoration: BoxDecoration(
                            color: statusColor.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(statusIcon, size: 11, color: statusColor),
                              const SizedBox(width: 3),
                              Text(statusLabel,
                                  style: TextStyle(
                                      fontSize: 11,
                                      color: statusColor,
                                      fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      isUnrecognized ? 'Tidak Dikenali' : prediction.speciesName,
                      style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A1A2E)),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 3),
                    Text(
                      'Keyakinan: ${prediction.confidencePercent}',
                      style: TextStyle(
                          fontSize: 12,
                          color: statusColor,
                          fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),
            const Padding(
              padding: EdgeInsets.only(right: 14),
              child: Icon(Icons.chevron_right_rounded,
                  color: Color(0xFFBDBDBD), size: 22),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Species stat model
// ─────────────────────────────────────────────────────────────────────────────
class _SpeciesStat {
  final String name;
  final int count;
  final double avgConfidence;

  const _SpeciesStat(
      {required this.name,
      required this.count,
      required this.avgConfidence});
}

// ─────────────────────────────────────────────────────────────────────────────
// Species breakdown card
// ─────────────────────────────────────────────────────────────────────────────
class _SpeciesBreakdown extends StatelessWidget {
  final List<_SpeciesStat> stats;
  final int total;

  const _SpeciesBreakdown({required this.stats, required this.total});

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
              offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Ringkasan per Spesies',
            style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1A1A2E)),
          ),
          const SizedBox(height: 14),
          ...stats.map((s) => _SpeciesRow(stat: s, total: total)),
        ],
      ),
    );
  }
}

class _SpeciesRow extends StatelessWidget {
  final _SpeciesStat stat;
  final int total;

  const _SpeciesRow({required this.stat, required this.total});

  @override
  Widget build(BuildContext context) {
    final isUnrecognized = stat.name == 'Tidak Dikenali';
    final color = isUnrecognized ? Colors.red.shade600 : const Color(0xFF1F6F43);
    final portion = total == 0 ? 0.0 : stat.count / total;

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  stat.name,
                  style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF1A1A2E)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${stat.count} foto  •  ${(stat.avgConfidence * 100).toStringAsFixed(1)}%',
                style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: color),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LayoutBuilder(
            builder: (_, constraints) => Stack(
              children: [
                Container(
                  height: 7,
                  width: constraints.maxWidth,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                Container(
                  height: 7,
                  width: constraints.maxWidth * portion.clamp(0.0, 1.0),
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
