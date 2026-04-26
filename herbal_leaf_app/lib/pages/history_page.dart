import 'dart:io';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../models/prediction.dart';
import '../providers/prediction_provider.dart';

class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});

  static final _dateFmt = DateFormat('dd MMM yyyy, HH:mm', 'id_ID');

  void _confirmDelete(BuildContext context, Prediction item) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Hapus Riwayat'),
        content: Text('Hapus hasil prediksi "${item.predictedClass}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              if (item.id != null) {
                context.read<PredictionProvider>().deletePrediction(item.id!);
              }
            },
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );
  }

  void _confirmClearAll(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Hapus Semua Riwayat'),
        content: const Text('Seluruh riwayat prediksi akan dihapus permanen.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<PredictionProvider>().clearHistory();
            },
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Hapus Semua'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F3),
      appBar: AppBar(
        title: const Text('Riwayat Klasifikasi'),
        actions: [
          Consumer<PredictionProvider>(
            builder: (context, provider, child) {
              if (provider.history.isEmpty) return const SizedBox.shrink();
              return IconButton(
                tooltip: 'Hapus semua',
                icon: const Icon(Icons.delete_sweep),
                onPressed: () => _confirmClearAll(context),
              );
            },
          ),
        ],
      ),
      body: Consumer<PredictionProvider>(
        builder: (context, provider, _) {
          final history = provider.history;

          if (history.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.history,
                    size: 64,
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Belum ada riwayat klasifikasi.',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.outline,
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: history.length,
            itemBuilder: (context, i) {
              final item = history[i];
              return _HistoryCard(
                item: item,
                dateFmt: _dateFmt,
                onDelete: () => _confirmDelete(context, item),
              );
            },
          );
        },
      ),
    );
  }
}

class _HistoryCard extends StatelessWidget {
  final Prediction item;
  final DateFormat dateFmt;
  final VoidCallback onDelete;

  const _HistoryCard({
    required this.item,
    required this.dateFmt,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final color = item.isRusak ? Colors.orange : Theme.of(context).colorScheme.primary;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // Thumbnail gambar
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: _buildThumbnail(item.imagePath),
            ),
            const SizedBox(width: 12),
            // Detail
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.predictedClass,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Keyakinan: ${item.confidencePercent}',
                    style: const TextStyle(fontSize: 13),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _formatDate(item.timestamp),
                    style: const TextStyle(fontSize: 11, color: Colors.black45),
                  ),
                ],
              ),
            ),
            // Status + delete
            Column(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    item.isRusak ? 'Rusak' : 'Sehat',
                    style: TextStyle(
                      fontSize: 11,
                      color: color,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                InkWell(
                  onTap: onDelete,
                  child: const Icon(Icons.delete_outline, size: 20, color: Colors.black38),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildThumbnail(String imagePath) {
    final file = File(imagePath);
    if (file.existsSync()) {
      return Image.file(
        file,
        width: 60,
        height: 60,
        fit: BoxFit.cover,
      );
    }
    return Builder(
      builder: (context) => Container(
        width: 60,
        height: 60,
        color: Theme.of(context).colorScheme.primaryContainer,
        child: Icon(
          Icons.local_florist,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    try {
      return dateFmt.format(dt.toLocal());
    } catch (_) {
      return dt.toString();
    }
  }
}
