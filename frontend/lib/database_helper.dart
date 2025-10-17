import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:intl/intl.dart';

class Recording {
  final int? id;
  final String text;
  final String createdAt;

  Recording({this.id, required this.text, required this.createdAt});

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'text': text,
      'createdAt': createdAt,
    };
  }
}

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('recordings.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        createdAt TEXT NOT NULL
      )
    ''');
  }

  Future<Recording> create(String text) async {
    final db = await instance.database;
    final formattedDate = DateFormat('yyyy-MM-dd HH:mm').format(DateTime.now());
    final recording = Recording(text: text, createdAt: formattedDate);
    final id = await db.insert('recordings', recording.toMap());
    return Recording(id: id, text: text, createdAt: formattedDate);
  }

  Future<List<Recording>> readAllRecordings() async {
    final db = await instance.database;
    final result = await db.query('recordings', orderBy: 'id DESC');
    return result.map((json) => Recording(
      id: json['id'] as int,
      text: json['text'] as String,
      createdAt: json['createdAt'] as String,
    )).toList();
  }

  Future<int> delete(int id) async {
    final db = await instance.database;
    return await db.delete(
      'recordings',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future close() async {
    final db = await instance.database;
    db.close();
  }
}