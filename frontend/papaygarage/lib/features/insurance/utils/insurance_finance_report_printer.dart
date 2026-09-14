import 'dart:math';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import '../models/insurance_models.dart';

/// Generates and prints the Papay Garage Insurance Finance Report / Ledger PDF
/// matching the physical printed ledger format with per-row and overall totals.
Future<void> printInsuranceFinanceReport(
  BuildContext context,
  InsuranceFinanceReport report, {
  DateTime? startDate,
  DateTime? endDate,
}) async {
  final fontRegular = await PdfGoogleFonts.cairoRegular();
  final fontBold = await PdfGoogleFonts.cairoBold();

  // Determine formatted date string for header
  String dateHeaderStr;
  if (startDate != null && endDate != null) {
    final sStr = DateFormat('dd/MM/yyyy').format(startDate);
    final eStr = DateFormat('dd/MM/yyyy').format(endDate);
    if (sStr == eStr) {
      dateHeaderStr = 'DATE $sStr';
    } else {
      dateHeaderStr = 'DATE $sStr - $eStr';
    }
  } else if (startDate != null) {
    dateHeaderStr = 'DATE FROM ${DateFormat('dd/MM/yyyy').format(startDate)}';
  } else if (endDate != null) {
    dateHeaderStr = 'DATE UNTIL ${DateFormat('dd/MM/yyyy').format(endDate)}';
  } else {
    dateHeaderStr = 'DATE ${DateFormat('dd/MM/yyyy').format(DateTime.now())}';
  }

  final pdf = pw.Document();

  final expenses = report.expenses;
  final incomes = report.incomes;
  final rowCount = max(max(expenses.length, incomes.length), 25);

  pdf.addPage(
    pw.MultiPage(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      header: (pw.Context ctx) => pw.Column(
        children: [
          pw.Center(
            child: pw.Text(
              'PAPAY GARAGE',
              style: pw.TextStyle(
                font: fontBold,
                fontSize: 20,
                fontWeight: pw.FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
          ),
          pw.SizedBox(height: 4),
          pw.Center(
            child: pw.Text(
              dateHeaderStr,
              style: pw.TextStyle(
                font: fontBold,
                fontSize: 12,
                fontWeight: pw.FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ),
          pw.SizedBox(height: 14),
        ],
      ),
      build: (pw.Context ctx) {
        final tableRows = <pw.TableRow>[];

        // Header Row
        tableRows.add(
          pw.TableRow(
            decoration: const pw.BoxDecoration(
              color: PdfColors.grey200,
            ),
            children: [
              _headerCell('Date', fontBold, width: 55),
              _headerCell('Expenses\nDescription', fontBold),
              _headerCell('QTR', fontBold, width: 48),
              _headerCell('Income\nDescription', fontBold),
              _headerCell('QTR', fontBold, width: 48),
              _headerCell('Total\n(QTR)', fontBold, width: 55),
            ],
          ),
        );

        // Data / Ruled Rows
        for (int i = 0; i < rowCount; i++) {
          final exp = i < expenses.length ? expenses[i] : null;
          final inc = i < incomes.length ? incomes[i] : null;

          String dateText = '';
          if (exp != null) {
            dateText = DateFormat('dd/MM/yyyy').format(exp.createdAt);
          } else if (inc != null) {
            dateText = DateFormat('dd/MM/yyyy').format(inc.createdAt);
          }

          final expDesc = exp?.description ?? '';
          final expPrice = exp != null ? exp.price.toStringAsFixed(2) : '';
          final incDesc = inc?.description ?? '';
          final incPrice = inc != null ? inc.price.toStringAsFixed(2) : '';

          String totalText = '';
          PdfColor totalColor = PdfColors.black;
          if (exp != null || inc != null) {
            final diff = (inc?.price ?? 0.0) - (exp?.price ?? 0.0);
            if (diff > 0) {
              totalText = '+${diff.toStringAsFixed(2)}';
              totalColor = PdfColors.green800;
            } else if (diff < 0) {
              totalText = '-${diff.abs().toStringAsFixed(2)}';
              totalColor = PdfColors.red800;
            } else {
              totalText = '0.00';
              totalColor = PdfColors.black;
            }
          }

          tableRows.add(
            pw.TableRow(
              children: [
                _dataCell(dateText, fontRegular, align: pw.TextAlign.center),
                _dataCell(expDesc, fontRegular, align: pw.TextAlign.left),
                _dataCell(expPrice, fontRegular, align: pw.TextAlign.right),
                _dataCell(incDesc, fontRegular, align: pw.TextAlign.left),
                _dataCell(incPrice, fontRegular, align: pw.TextAlign.right),
                _dataCell(
                  totalText,
                  fontBold,
                  align: pw.TextAlign.right,
                  color: totalColor,
                ),
              ],
            ),
          );
        }

        // Totals Row
        tableRows.add(
          pw.TableRow(
            decoration: const pw.BoxDecoration(
              color: PdfColors.grey100,
            ),
            children: [
              _totalCell('', fontBold),
              _totalCell('TOTAL EXPENSES', fontBold, align: pw.TextAlign.right),
              _totalCell(report.totalExpense.toStringAsFixed(2), fontBold, align: pw.TextAlign.right),
              _totalCell('TOTAL INCOME', fontBold, align: pw.TextAlign.right),
              _totalCell(report.totalIncome.toStringAsFixed(2), fontBold, align: pw.TextAlign.right),
              _totalCell(
                '${report.net >= 0 ? '+' : '-'}${report.net.abs().toStringAsFixed(2)}',
                fontBold,
                align: pw.TextAlign.right,
                color: report.net >= 0 ? PdfColors.green800 : PdfColors.red800,
              ),
            ],
          ),
        );

        return [
          pw.Table(
            border: pw.TableBorder.all(color: PdfColors.black, width: 0.8),
            columnWidths: const {
              0: pw.FixedColumnWidth(55),
              1: pw.FlexColumnWidth(2.2),
              2: pw.FixedColumnWidth(48),
              3: pw.FlexColumnWidth(2.2),
              4: pw.FixedColumnWidth(48),
              5: pw.FixedColumnWidth(55),
            },
            children: tableRows,
          ),
          pw.SizedBox(height: 12),
          pw.Container(
            padding: const pw.EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: pw.BoxDecoration(
              border: pw.Border.all(color: PdfColors.black, width: 0.8),
              color: PdfColors.grey100,
            ),
            child: pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text(
                  'NET PROFIT / BALANCE (صافي الربح / الرصيد):',
                  style: pw.TextStyle(
                    font: fontBold,
                    fontSize: 10.5,
                    fontWeight: pw.FontWeight.bold,
                  ),
                ),
                pw.Text(
                  '${report.net >= 0 ? '+' : '-'}${report.net.abs().toStringAsFixed(2)} QTR',
                  style: pw.TextStyle(
                    font: fontBold,
                    fontSize: 11,
                    fontWeight: pw.FontWeight.bold,
                    color: report.net >= 0 ? PdfColors.green900 : PdfColors.red900,
                  ),
                ),
              ],
            ),
          ),
        ];
      },
    ),
  );

  final printFileName =
      'papay-insurance-report-${DateFormat('yyyyMMdd').format(startDate ?? DateTime.now())}';
  await Printing.layoutPdf(
    onLayout: (_) async => pdf.save(),
    name: printFileName,
  );
}

pw.Widget _headerCell(
  String text,
  pw.Font fontBold, {
  double? width,
}) {
  return pw.Container(
    height: 32,
    alignment: pw.Alignment.center,
    padding: const pw.EdgeInsets.symmetric(horizontal: 4, vertical: 2),
    child: pw.Text(
      text,
      textAlign: pw.TextAlign.center,
      style: pw.TextStyle(
        font: fontBold,
        fontSize: 9,
        fontWeight: pw.FontWeight.bold,
      ),
    ),
  );
}

pw.Widget _dataCell(
  String text,
  pw.Font fontRegular, {
  pw.TextAlign align = pw.TextAlign.left,
  PdfColor? color,
}) {
  return pw.Container(
    height: 20,
    alignment: align == pw.TextAlign.center
        ? pw.Alignment.center
        : align == pw.TextAlign.right
            ? pw.Alignment.centerRight
            : pw.Alignment.centerLeft,
    padding: const pw.EdgeInsets.symmetric(horizontal: 4, vertical: 2),
    child: pw.Text(
      text,
      textAlign: align,
      maxLines: 1,
      overflow: pw.TextOverflow.clip,
      style: pw.TextStyle(
        font: fontRegular,
        fontSize: 8.5,
        color: color ?? PdfColors.black,
      ),
    ),
  );
}

pw.Widget _totalCell(
  String text,
  pw.Font fontBold, {
  pw.TextAlign align = pw.TextAlign.left,
  PdfColor? color,
}) {
  return pw.Container(
    height: 24,
    alignment: align == pw.TextAlign.right ? pw.Alignment.centerRight : pw.Alignment.centerLeft,
    padding: const pw.EdgeInsets.symmetric(horizontal: 4, vertical: 2),
    child: pw.Text(
      text,
      textAlign: align,
      style: pw.TextStyle(
        font: fontBold,
        fontSize: 8.5,
        fontWeight: pw.FontWeight.bold,
        color: color ?? PdfColors.black,
      ),
    ),
  );
}
