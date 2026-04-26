// import 'dart:io';
// import 'package:flutter/material.dart';
// import 'package:image_picker/image_picker.dart';
// import 'package:provider/provider.dart';
// import '../providers/prediction_provider.dart';
// import '../models/prediction.dart';
// import '../data/plant_data.dart';
// import '../widgets/stat_card.dart';
// import '../widgets/plant_card.dart';
// import 'result_page.dart';
// import 'plant_detail_page.dart';

// class HomePage extends StatelessWidget {
//   const HomePage({super.key});

//   Future<void> _pickAndPredict(BuildContext context, ImageSource source) async {
//     final picker = ImagePicker();
//     final picked = await picker.pickImage(
//       source: source,
//       imageQuality: 85,
//       maxWidth: 1024,
//     );
//     if (picked == null) return;

//     if (!context.mounted) return;
//     await context.read<PredictionProvider>().predictImage(File(picked.path));

//     if (!context.mounted) return;
//     final provider = context.read<PredictionProvider>();
//     if (provider.state == PredictionState.success &&
//         provider.lastResult != null) {
//       _showResult(context, provider.lastResult!, File(picked.path));
//     } else if (provider.state == PredictionState.error) {
//       _showErrorSnackbar(
//         context,
//         provider.errorMessage ?? 'Terjadi kesalahan.',
//       );
//     }
//   }

//   void _showSourceSheet(BuildContext context) {
//     showModalBottomSheet(
//       context: context,
//       shape: const RoundedRectangleBorder(
//         borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
//       ),
//       builder: (ctx) => SafeArea(
//         child: Column(
//           mainAxisSize: MainAxisSize.min,
//           children: [
//             const SizedBox(height: 12),
//             Container(
//               width: 40,
//               height: 4,
//               decoration: BoxDecoration(
//                 color: Theme.of(ctx).colorScheme.outlineVariant,
//                 borderRadius: BorderRadius.circular(2),
//               ),
//             ),
//             const SizedBox(height: 16),
//             const Text(
//               'Pilih Sumber Gambar',
//               style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
//             ),
//             const SizedBox(height: 8),
//             ListTile(
//               leading: CircleAvatar(
//                 backgroundColor: Theme.of(ctx).colorScheme.primaryContainer,
//                 child: Icon(
//                   Icons.camera_alt,
//                   color: Theme.of(ctx).colorScheme.primary,
//                 ),
//               ),
//               title: const Text('Kamera'),
//               onTap: () {
//                 Navigator.pop(ctx);
//                 _pickAndPredict(context, ImageSource.camera);
//               },
//             ),
//             ListTile(
//               leading: CircleAvatar(
//                 backgroundColor: Theme.of(ctx).colorScheme.primaryContainer,
//                 child: Icon(
//                   Icons.photo_library,
//                   color: Theme.of(ctx).colorScheme.primary,
//                 ),
//               ),
//               title: const Text('Galeri'),
//               onTap: () {
//                 Navigator.pop(ctx);
//                 _pickAndPredict(context, ImageSource.gallery);
//               },
//             ),
//             const SizedBox(height: 12),
//           ],
//         ),
//       ),
//     );
//   }

//   void _showResult(BuildContext context, Prediction result, File imageFile) {
//     Navigator.push(
//       context,
//       MaterialPageRoute(
//         builder: (_) => ResultPage(result: result, imageFile: imageFile),
//       ),
//     );
//   }

//   void _showErrorSnackbar(BuildContext context, String message) {
//     ScaffoldMessenger.of(context).showSnackBar(
//       SnackBar(
//         content: Text(message),
//         backgroundColor: Colors.red.shade700,
//         behavior: SnackBarBehavior.floating,
//       ),
//     );
//   }

//   Widget _buildPlantGrid(BuildContext context) {
//     return FutureBuilder<void>(
//       // ⏳ tunda sedikit supaya frame pertama ringan
//       future: Future.delayed(const Duration(milliseconds: 50)),
//       builder: (context, snapshot) {
//         if (snapshot.connectionState != ConnectionState.done) {
//           return const Padding(
//             padding: EdgeInsets.all(24),
//             child: Center(child: CircularProgressIndicator()),
//           );
//         }

//         return GridView.builder(
//           shrinkWrap: true,
//           physics: const NeverScrollableScrollPhysics(),
//           gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
//             crossAxisCount: 2,
//             mainAxisSpacing: 16,
//             crossAxisSpacing: 16,
//             childAspectRatio: 1.1,
//           ),
//           itemCount: kHerbalPlants.length,
//           itemBuilder: (_, i) {
//             final plant = kHerbalPlants[i];
//             return PlantCard(
//               name: plant.name,
//               latin: plant.latinName,
//               iconPath: plant.iconPath,
//               onTap: () {
//                 Navigator.push(
//                   context,
//                   MaterialPageRoute(
//                     builder: (_) => PlantDetailPage(plant: plant),
//                   ),
//                 );
//               },
//             );
//           },
//         );
//       },
//     );
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       backgroundColor: const Color(0xFFF6F8F3),
//       appBar: AppBar(
//         title: const Text(
//           'HerbalScan',
//           style: TextStyle(fontWeight: FontWeight.bold),
//         ),
//       ),
//       body: Consumer<PredictionProvider>(
//         builder: (context, provider, _) {
//           final isLoading = provider.state == PredictionState.loading;

//           return SingleChildScrollView(
//             padding: const EdgeInsets.all(16),
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 Text(
//                   'Identifikasi Daun Herbal dengan AI',
//                   style: Theme.of(context).textTheme.bodyMedium?.copyWith(
//                     color: Theme.of(context).colorScheme.onSurfaceVariant,
//                   ),
//                 ),
//                 const SizedBox(height: 16),

//                 // Stat Cards
//                 Row(
//                   mainAxisAlignment: MainAxisAlignment.spaceBetween,
//                   children: [
//                     StatCard(
//                       title: 'Jenis Daun',
//                       value: '${kHerbalPlants.length}',
//                     ),
//                     const StatCard(title: 'Akurasi', value: '~98%'),
//                     StatCard(
//                       title: 'Riwayat',
//                       value: provider.state == PredictionState.loading
//                           ? '-'
//                           : '${provider.history.length}',
//                     ),
//                   ],
//                 ),
//                 const SizedBox(height: 24),

//                 // Upload Card
//                 Center(
//                   child: Card(
//                     elevation: 0,
//                     color: Theme.of(context).colorScheme.surfaceContainerLow,
//                     shape: RoundedRectangleBorder(
//                       borderRadius: BorderRadius.circular(16),
//                     ),
//                     child: Padding(
//                       padding: const EdgeInsets.all(20),
//                       child: Column(
//                         crossAxisAlignment: CrossAxisAlignment.center,
//                         children: [
//                           CircleAvatar(
//                             radius: 32,
//                             backgroundColor: Theme.of(
//                               context,
//                             ).colorScheme.primary,
//                             child: isLoading
//                                 ? const CircularProgressIndicator(
//                                     color: Colors.white,
//                                     strokeWidth: 2.5,
//                                   )
//                                 : const Icon(
//                                     Icons.camera_alt,
//                                     color: Colors.white,
//                                     size: 32,
//                                   ),
//                           ),
//                           const SizedBox(height: 12),
//                           const Text(
//                             'Scan Daun Herbal',
//                             style: TextStyle(
//                               fontSize: 18,
//                               fontWeight: FontWeight.bold,
//                             ),
//                           ),
//                           const SizedBox(height: 4),
//                           const Text(
//                             'Ambil foto atau pilih dari galeri',
//                             textAlign: TextAlign.center,
//                             style: TextStyle(color: Colors.black54),
//                           ),
//                           const SizedBox(height: 16),
//                           FilledButton.icon(
//                             onPressed: isLoading
//                                 ? null
//                                 : () => _showSourceSheet(context),
//                             icon: const Icon(Icons.image_search),
//                             label: Text(
//                               isLoading ? 'Memproses...' : 'Pilih Gambar',
//                             ),
//                           ),
//                         ],
//                       ),
//                     ),
//                   ),
//                 ),
//                 const SizedBox(height: 24),

//                 // Database tanaman
//                 Text(
//                   'Database Daun Herbal',
//                   style: Theme.of(context).textTheme.titleMedium?.copyWith(
//                     fontWeight: FontWeight.bold,
//                   ),
//                 ),
//                 const SizedBox(height: 16),

//                 _buildPlantGrid(context),
//               ],
//             ),
//           );
//         },
//       ),
//     );
//   }
// }

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../providers/prediction_provider.dart';
import '../models/prediction.dart';
import '../data/plant_data.dart';
import '../widgets/stat_card.dart';
import '../widgets/plant_card.dart';
import 'result_page.dart';
import 'plant_detail_page.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  // =============================
  // PICK IMAGE & PREDICT
  // =============================
  Future<void> _pickAndPredict(BuildContext context, ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1024,
    );
    if (picked == null) return;

    if (!context.mounted) return;

    await context.read<PredictionProvider>().predictImage(File(picked.path));

    if (!context.mounted) return;

    final provider = context.read<PredictionProvider>();
    if (provider.state == PredictionState.success &&
        provider.lastResult != null) {
      _showResult(context, provider.lastResult!, File(picked.path));
    } else if (provider.state == PredictionState.error) {
      _showErrorSnackbar(
        context,
        provider.errorMessage ?? 'Terjadi kesalahan.',
      );
    }
  }

  // =============================
  // SOURCE SHEET
  // =============================
  void _showSourceSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Theme.of(ctx).colorScheme.outlineVariant,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Pilih Sumber Gambar',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ListTile(
              leading: CircleAvatar(
                backgroundColor: Theme.of(ctx).colorScheme.primaryContainer,
                child: Icon(
                  Icons.camera_alt,
                  color: Theme.of(ctx).colorScheme.primary,
                ),
              ),
              title: const Text('Kamera'),
              onTap: () {
                Navigator.pop(ctx);
                _pickAndPredict(context, ImageSource.camera);
              },
            ),
            ListTile(
              leading: CircleAvatar(
                backgroundColor: Theme.of(ctx).colorScheme.primaryContainer,
                child: Icon(
                  Icons.photo_library,
                  color: Theme.of(ctx).colorScheme.primary,
                ),
              ),
              title: const Text('Galeri'),
              onTap: () {
                Navigator.pop(ctx);
                _pickAndPredict(context, ImageSource.gallery);
              },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  // =============================
  // RESULT PAGE
  // =============================
  void _showResult(BuildContext context, Prediction result, File imageFile) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(result: result, imageFile: imageFile),
      ),
    );
  }

  // =============================
  // ERROR SNACKBAR
  // =============================
  void _showErrorSnackbar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red.shade700,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  // =============================
  // DEFERRED GRID (ANTI FREEZE)
  // =============================
  Widget _buildPlantGrid(BuildContext context) {
    return FutureBuilder<void>(
      // ⏳ tunda sedikit supaya frame pertama ringan
      future: Future.delayed(const Duration(milliseconds: 50)),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Padding(
            padding: EdgeInsets.all(24),
            child: Center(child: CircularProgressIndicator()),
          );
        }

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 1.1,
          ),
          itemCount: kHerbalPlants.length,
          itemBuilder: (_, i) {
            final plant = kHerbalPlants[i];
            return PlantCard(
              name: plant.name,
              latin: plant.latinName,
              iconPath: plant.iconPath,
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PlantDetailPage(plant: plant),
                  ),
                );
              },
            );
          },
        );
      },
    );
  }

  // =============================
  // BUILD UI
  // =============================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F3),
      appBar: AppBar(
        title: const Text(
          'HerbalScan',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: Consumer<PredictionProvider>(
        builder: (context, provider, _) {
          final isLoading = provider.state == PredictionState.loading;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Identifikasi Daun Herbal dengan AI',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 16),

                // =============================
                // STAT CARDS
                // =============================
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    StatCard(
                      title: 'Jenis Daun',
                      value: '${kHerbalPlants.length}',
                    ),
                    const StatCard(title: 'Akurasi', value: '~98%'),
                    StatCard(
                      title: 'Riwayat',
                      value: provider.state == PredictionState.loading
                          ? '-'
                          : '${provider.history.length}',
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // =============================
                // UPLOAD CARD
                // =============================
                Center(
                  child: Card(
                    elevation: 0,
                    color: Theme.of(context).colorScheme.surfaceContainerLow,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          CircleAvatar(
                            radius: 32,
                            backgroundColor: Theme.of(
                              context,
                            ).colorScheme.primary,
                            child: isLoading
                                ? const CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2.5,
                                  )
                                : const Icon(
                                    Icons.camera_alt,
                                    color: Colors.white,
                                    size: 32,
                                  ),
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'Scan Daun Herbal',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Ambil foto atau pilih dari galeri',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.black54),
                          ),
                          const SizedBox(height: 16),
                          FilledButton.icon(
                            onPressed: isLoading
                                ? null
                                : () => _showSourceSheet(context),
                            icon: const Icon(Icons.image_search),
                            label: Text(
                              isLoading ? 'Memproses...' : 'Pilih Gambar',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // =============================
                // DATABASE TANAMAN
                // =============================
                Text(
                  'Database Daun Herbal',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),

                // ✅ GRID YANG DITUNDA
                _buildPlantGrid(context),
              ],
            ),
          );
        },
      ),
    );
  }
}
