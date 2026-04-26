import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;
import '../models/prediction.dart';

class DatabaseService {
  static const _dbName = 'herbalscan.db';
  static const _dbVersion = 1;
  static const _table = 'predictions';

  DatabaseService._();
  static final DatabaseService instance = DatabaseService._();

  Database? _db;

  Future<Database> get _database async {
    _db ??= await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, _dbName);
    return openDatabase(
      path,
      version: _dbVersion,
      onCreate: (db, _) async {
        await db.execute('''
          CREATE TABLE $_table (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path       TEXT    NOT NULL,
            predicted_class  TEXT    NOT NULL,
            confidence_score REAL    NOT NULL,
            timestamp        TEXT    NOT NULL
          )
        ''');
      },
    );
  }

  Future<int> insertPrediction(Prediction prediction) async {
    final db = await _database;
    return db.insert(
      _table,
      prediction.toMap()..remove('id'),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Prediction>> getAllPredictions() async {
    final db = await _database;
    final rows = await db.query(_table, orderBy: 'id DESC');
    return rows.map((r) => Prediction.fromJson(r)).toList();
  }

  Future<int> deletePrediction(int id) async {
    final db = await _database;
    return db.delete(_table, where: 'id = ?', whereArgs: [id]);
  }

  Future<void> clearAll() async {
    final db = await _database;
    await db.delete(_table);
  }
}
