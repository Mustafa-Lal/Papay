import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import '../models/insurance_models.dart';

const _gold = PdfColor.fromInt(0xFFC49F38);
const _indigo = PdfColor.fromInt(0xFF3F51B5);
const _headerBg = PdfColor.fromInt(0xFFF0EDE6); // very light warm grey header

/// Generates and prints a Papay Garage insurance invoice PDF.
Future<void> printInsuranceInvoice(
  BuildContext context,
  InsuranceInvoice invoice,
) async {
  final arabicFont = await PdfGoogleFonts.cairoRegular();
  final arabicFontBold = await PdfGoogleFonts.cairoBold();

  final pdf = pw.Document();
  final invoiceNumber =
      '${DateFormat('yyMMdd').format(invoice.createdAt)}-${invoice.id.toString().padLeft(3, '0')}';
  final dateStr = DateFormat('dd/MM/yyyy').format(invoice.createdAt);

  pdf.addPage(
    pw.Page(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.symmetric(horizontal: 40, vertical: 36),
      build: (pw.Context ctx) => pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          _header(arabicFont, arabicFontBold),
          pw.SizedBox(height: 12),
          pw.Divider(thickness: 1.5, color: PdfColors.black),
          pw.SizedBox(height: 10),
          _invoiceMeta(dateStr, invoiceNumber, invoice, arabicFont, arabicFontBold),
          pw.SizedBox(height: 14),
          pw.Divider(thickness: 0.8, color: PdfColors.grey500),
          pw.SizedBox(height: 10),
          _itemsTable(invoice, arabicFont, arabicFontBold),
          pw.Spacer(),
          _signatures(arabicFont),
        ],
      ),
    ),
  );

  await Printing.layoutPdf(
    onLayout: (_) async => pdf.save(),
    name: 'Invoice-$invoiceNumber',
  );
}

// ── Arabic text helper ────────────────────────────────────────────────────────
pw.Widget _ar(
  String text,
  pw.Font font, {
  double size = 8,
  PdfColor? color,
  bool bold = false,
  pw.Font? boldFont,
}) {
  return pw.Text(
    text,
    textDirection: pw.TextDirection.rtl,
    style: pw.TextStyle(
      font: bold && boldFont != null ? boldFont : font,
      fontSize: size,
      color: color ?? PdfColors.black,
    ),
  );
}

// ── Header ────────────────────────────────────────────────────────────────────
// Every line is constrained to the same fixed height so both columns
// have identical total heights regardless of font metrics.
pw.Widget _header(pw.Font arFont, pw.Font arBold) {
  const titleH = 17.0;  // height for bold title line
  const lineH  = 11.0;  // height for each info line

  const enBoldStyle  = pw.TextStyle(fontSize: 13, fontWeight: pw.FontWeight.bold);
  const enSmallStyle = pw.TextStyle(fontSize: 8,  color: PdfColors.grey700);

  pw.Widget enLine(String t, {bool bold = false}) => pw.SizedBox(
        height: bold ? titleH : lineH,
        child: pw.Align(
          alignment: pw.Alignment.centerLeft,
          child: pw.Text(t, style: bold ? enBoldStyle : enSmallStyle),
        ),
      );

  pw.Widget arLine(String t, {bool bold = false}) => pw.SizedBox(
        height: bold ? titleH : lineH,
        child: pw.Align(
          alignment: pw.Alignment.centerRight,
          child: pw.Text(
            t,
            textDirection: pw.TextDirection.rtl,
            style: pw.TextStyle(
              font: bold ? arBold : arFont,
              fontSize: bold ? 13 : 8,
              color: bold ? PdfColors.black : PdfColors.grey700,
            ),
          ),
        ),
      );

  return pw.Row(
    mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
    crossAxisAlignment: pw.CrossAxisAlignment.start,
    children: [
      pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
        enLine('Papay Garage', bold: true),
        enLine('Mobile: 77001732'),
        enLine('Tel.: 70060019'),
        enLine('P.O. Box: 40701'),
        enLine('Garage No.: 133'),
        enLine('Street No.: 21'),
        enLine('Industrial Area'),
        enLine('Doha - Qatar'),
      ]),
      pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.end, children: [
        arLine('كراج باباي', bold: true),
        arLine('جوال: 77001732'),
        arLine('تليفون: 70060019'),
        arLine('ص.ب: 40701'),
        arLine('كراج رقم: 133'),
        arLine('شارع رقم: 21'),
        arLine('المنطقة الصناعية'),
        arLine('الدوحة - قطر'),
      ]),
    ],
  );
}


// ── Invoice Meta ──────────────────────────────────────────────────────────────
pw.Widget _invoiceMeta(
  String dateStr,
  String invoiceNumber,
  InsuranceInvoice invoice,
  pw.Font arFont,
  pw.Font arBold,
) {
  final customer = invoice.customer;
  const enSmall = pw.TextStyle(fontSize: 9, color: PdfColors.grey600);
  const enBold10 = pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold);
  const titleStyle = pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, letterSpacing: 2);

  return pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
    pw.Row(
      mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
      children: [
        pw.Text('INVOICE', style: titleStyle),
        pw.Row(children: [
          pw.Text('Date: ', style: enSmall),
          pw.Text(dateStr, style: enBold10),
        ]),
        _ar('فاتورة', arFont, size: 14, bold: true, boldFont: arBold),
      ],
    ),
    pw.SizedBox(height: 8),
    pw.Row(children: [
      pw.Text('No: ', style: enSmall),
      pw.Text(invoiceNumber,
          style: const pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold, color: _indigo)),
    ]),
    pw.SizedBox(height: 5),
    pw.Text('MR. / MESSERS', style: enSmall),
    pw.SizedBox(height: 2),
    pw.Text(
      '${invoice.plateNumber}  --  ${customer.customerName ?? 'Unknown'}'
      '${customer.phoneNumber != null ? '  (Tel: ${customer.phoneNumber})' : ''}',
      style: enBold10,
    ),
  ]);
}

// ── Items Table ───────────────────────────────────────────────────────────────
pw.Widget _itemsTable(InsuranceInvoice invoice, pw.Font arFont, pw.Font arBold) {
  // Column header - light warm background, dark text (not white-on-black)
  final headerEN = pw.TextStyle(fontSize: 9, fontWeight: pw.FontWeight.bold, color: PdfColors.black);
  final headerAR = pw.TextStyle(font: arFont, fontSize: 7, color: PdfColors.grey700);

  pw.Widget hCell(String en, String ar, {pw.TextAlign align = pw.TextAlign.center}) =>
      pw.Container(
        padding: const pw.EdgeInsets.symmetric(horizontal: 6, vertical: 7),
        child: pw.Column(mainAxisSize: pw.MainAxisSize.min, children: [
          pw.Text(en, style: headerEN, textAlign: align),
          pw.SizedBox(height: 1),
          pw.Text(ar, style: headerAR, textDirection: pw.TextDirection.rtl, textAlign: align),
        ]),
      );

  pw.Widget cell(
    String text, {
    bool bold = false,
    pw.TextAlign align = pw.TextAlign.center,
    PdfColor? color,
    double fontSize = 10,
  }) =>
      pw.Padding(
        padding: const pw.EdgeInsets.symmetric(horizontal: 6, vertical: 9),
        child: pw.Text(text,
            textAlign: align,
            style: pw.TextStyle(
              fontSize: fontSize,
              fontWeight: bold ? pw.FontWeight.bold : pw.FontWeight.normal,
              color: color,
            )),
      );

  final itemRows = <pw.TableRow>[];

  // Header row - light background, no dark highlight
  itemRows.add(pw.TableRow(
    decoration: const pw.BoxDecoration(color: _headerBg),
    children: [
      hCell('ITEM', 'الرقم'),
      hCell('DESCRIPTION', 'التفاصيل', align: pw.TextAlign.left),
      hCell('QTY', 'الكمية'),
      hCell('UNIT PRICE\n(QR)', 'سعر الوحدة'),
      hCell('AMOUNT\n(QR)', 'المبلغ', align: pw.TextAlign.right),
    ],
  ));

  // Item rows (plain white)
  for (var i = 0; i < invoice.items.length; i++) {
    final item = invoice.items[i];
    final printUnitPrice =
        item.unitPrice + (item.quantity > 0 ? item.commission / item.quantity : 0);

    itemRows.add(pw.TableRow(children: [
      cell('${i + 1}', bold: true, color: _gold),
      cell(item.description, bold: true, align: pw.TextAlign.left),
      cell('${item.quantity.toInt()}', bold: true, color: _gold),
      cell(printUnitPrice.toStringAsFixed(2)),
      cell(item.total.toStringAsFixed(2), bold: true, align: pw.TextAlign.right),
    ]));
  }

  // Papay Charges row
  itemRows.add(pw.TableRow(children: [
    cell('-'),
    pw.Padding(
      padding: const pw.EdgeInsets.symmetric(horizontal: 6, vertical: 9),
      child: pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
        pw.Text('Papay Charges',
            style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold, color: _gold)),
        pw.SizedBox(height: 1),
        pw.Text('رسوم باباي',
            textDirection: pw.TextDirection.rtl,
            style: pw.TextStyle(font: arFont, fontSize: 7, color: PdfColors.grey600)),
      ]),
    ),
    pw.SizedBox(),
    pw.SizedBox(),
    cell(invoice.laborCharges.toStringAsFixed(2), bold: true, align: pw.TextAlign.right),
  ]));

  final columnWidths = {
    0: const pw.FixedColumnWidth(36),   // Item #
    1: const pw.FlexColumnWidth(4),     // Description
    2: const pw.FixedColumnWidth(36),   // Qty
    3: const pw.FixedColumnWidth(80),   // Unit Price
    4: const pw.FixedColumnWidth(80),   // Amount
  };

  // Build the table for items + papay charges
  final table = pw.Table(
    border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.5),
    columnWidths: columnWidths,
    children: itemRows,
  );

  // TOTAL ONLY row - rendered OUTSIDE the table as a full-width Row
  // so the label can span naturally and the amount aligns to the right
  final totalRow = pw.Container(
    decoration: pw.BoxDecoration(
      border: pw.Border.all(color: PdfColors.grey400, width: 0.5),
    ),
    child: pw.Row(
      children: [
        pw.Expanded(
          child: pw.Padding(
            padding: const pw.EdgeInsets.symmetric(horizontal: 8, vertical: 12),
            child: pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
              pw.Text('TOTAL',
                  style: const pw.TextStyle(fontSize: 11, fontWeight: pw.FontWeight.bold)),
              pw.SizedBox(height: 2),
              pw.Text('المجموع فقط وقدره',
                  textDirection: pw.TextDirection.rtl,
                  style: pw.TextStyle(font: arFont, fontSize: 8, color: PdfColors.grey700)),
            ]),
          ),
        ),
        pw.Container(
          width: 80,
          padding: const pw.EdgeInsets.symmetric(horizontal: 8, vertical: 12),
          child: pw.Text(
            'QR ${invoice.grandTotal.toStringAsFixed(2)}',
            textAlign: pw.TextAlign.right,
            style: const pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold, color: _gold),
          ),
        ),
      ],
    ),
  );

  return pw.Column(children: [table, totalRow]);
}

// ── Signatures ────────────────────────────────────────────────────────────────
pw.Widget _signatures(pw.Font arFont) {
  const enSmall = pw.TextStyle(fontSize: 9, color: PdfColors.grey700);
  final arSmall = pw.TextStyle(font: arFont, fontSize: 9, color: PdfColors.grey700);

  pw.Widget sig(String arLabel, String enLabel) => pw.Column(children: [
        pw.Container(
          width: 160,
          decoration: const pw.BoxDecoration(
            border: pw.Border(
              bottom: pw.BorderSide(
                style: pw.BorderStyle.dashed,
                color: PdfColors.grey500,
                width: 0.8,
              ),
            ),
          ),
          height: 1,
        ),
        pw.SizedBox(height: 6),
        pw.Text(arLabel, textDirection: pw.TextDirection.rtl, style: arSmall),
        pw.Text(enLabel, style: enSmall),
      ]);

  return pw.Row(
    mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
    children: [
      sig('توقيع المستلم', "RECEIVER'S SIGN."),
      sig('توقيع المدير', "MANAGER'S SIGN."),
    ],
  );
}
