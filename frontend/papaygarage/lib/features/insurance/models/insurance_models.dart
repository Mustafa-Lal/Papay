enum PaymentStatus { unpaid, partiallyPaid, paid }

PaymentStatus paymentStatusFromString(String s) {
  switch (s.toUpperCase()) {
    case 'PAID':
      return PaymentStatus.paid;
    case 'PARTIALLY_PAID':
      return PaymentStatus.partiallyPaid;
    default:
      return PaymentStatus.unpaid;
  }
}

String paymentStatusToString(PaymentStatus s) {
  switch (s) {
    case PaymentStatus.paid:
      return 'PAID';
    case PaymentStatus.partiallyPaid:
      return 'PARTIALLY_PAID';
    case PaymentStatus.unpaid:
      return 'UNPAID';
  }
}

String paymentStatusLabel(PaymentStatus s) {
  switch (s) {
    case PaymentStatus.paid:
      return 'Paid';
    case PaymentStatus.partiallyPaid:
      return 'Partially Paid';
    case PaymentStatus.unpaid:
      return 'Unpaid';
  }
}

class InsuranceCustomer {
  final int id;
  final String? customerName;
  final String? phoneNumber;
  final String? qid;

  InsuranceCustomer({
    required this.id,
    this.customerName,
    this.phoneNumber,
    this.qid,
  });

  factory InsuranceCustomer.fromJson(Map<String, dynamic> json) {
    return InsuranceCustomer(
      id: json['id'] as int,
      customerName: json['customer_name'] as String?,
      phoneNumber: json['phone_number'] as String?,
      qid: json['qid'] as String?,
    );
  }
}

class InsuranceItem {
  final int id;
  final int invoiceId;
  final String description;
  final double quantity;
  final double unitPrice;
  final double commission;

  InsuranceItem({
    required this.id,
    required this.invoiceId,
    required this.description,
    required this.quantity,
    required this.unitPrice,
    required this.commission,
  });

  factory InsuranceItem.fromJson(Map<String, dynamic> json) {
    return InsuranceItem(
      id: json['id'] as int,
      invoiceId: json['invoice_id'] as int,
      description: json['description'] as String,
      quantity: double.parse(json['quantity'].toString()),
      unitPrice: double.parse(json['unit_price'].toString()),
      commission: double.parse(json['commission'].toString()),
    );
  }

  double get total => (quantity * unitPrice) + commission;
}

class InsuranceImage {
  final int id;
  final int invoiceId;
  final String imageType;
  final String filePath;

  InsuranceImage({
    required this.id,
    required this.invoiceId,
    required this.imageType,
    required this.filePath,
  });

  factory InsuranceImage.fromJson(Map<String, dynamic> json) {
    return InsuranceImage(
      id: json['id'] as int,
      invoiceId: json['invoice_id'] as int,
      imageType: json['image_type'] as String,
      filePath: json['file_path'] as String,
    );
  }
}

class InsuranceInvoice {
  final int id;
  final int customerId;
  final String plateNumber;
  final double laborCharges;
  final PaymentStatus paymentStatus;
  final int createdBy;
  final DateTime createdAt;
  final InsuranceCustomer customer;
  final List<InsuranceItem> items;
  final List<InsuranceImage> images;

  InsuranceInvoice({
    required this.id,
    required this.customerId,
    required this.plateNumber,
    required this.laborCharges,
    required this.paymentStatus,
    required this.createdBy,
    required this.createdAt,
    required this.customer,
    required this.items,
    required this.images,
  });

  factory InsuranceInvoice.fromJson(Map<String, dynamic> json) {
    return InsuranceInvoice(
      id: json['id'] as int,
      customerId: json['customer_id'] as int,
      plateNumber: json['plate_number'] as String,
      laborCharges: double.parse(json['labor_charges'].toString()),
      paymentStatus: paymentStatusFromString(json['payment_status'] as String),
      createdBy: json['created_by'] as int,
      createdAt: DateTime.parse(json['created_at'] as String),
      customer: InsuranceCustomer.fromJson(json['customer'] as Map<String, dynamic>),
      items: (json['items'] as List).map((e) => InsuranceItem.fromJson(e)).toList(),
      images: (json['images'] as List).map((e) => InsuranceImage.fromJson(e)).toList(),
    );
  }

  double get subtotal => items.fold(0, (sum, i) => sum + i.total);
  double get grandTotal => subtotal + laborCharges;

  InsuranceInvoice copyWith({
    int? id,
    int? customerId,
    String? plateNumber,
    double? laborCharges,
    PaymentStatus? paymentStatus,
    int? createdBy,
    DateTime? createdAt,
    InsuranceCustomer? customer,
    List<InsuranceItem>? items,
    List<InsuranceImage>? images,
  }) {
    return InsuranceInvoice(
      id: id ?? this.id,
      customerId: customerId ?? this.customerId,
      plateNumber: plateNumber ?? this.plateNumber,
      laborCharges: laborCharges ?? this.laborCharges,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      createdBy: createdBy ?? this.createdBy,
      createdAt: createdAt ?? this.createdAt,
      customer: customer ?? this.customer,
      items: items ?? this.items,
      images: images ?? this.images,
    );
  }
}

class InsuranceInvoiceSummary {
  final int customerId;
  final String? name;
  final String? phoneNumber;
  final int invoiceId;
  final String plateNumber;
  final PaymentStatus paymentStatus;
  final DateTime invoiceDate;

  InsuranceInvoiceSummary({
    required this.customerId,
    this.name,
    this.phoneNumber,
    required this.invoiceId,
    required this.plateNumber,
    required this.paymentStatus,
    required this.invoiceDate,
  });

  factory InsuranceInvoiceSummary.fromJson(Map<String, dynamic> json) {
    return InsuranceInvoiceSummary(
      customerId: json['customer_id'] as int,
      name: json['name'] as String?,
      phoneNumber: json['phone_number'] as String?,
      invoiceId: json['invoice_id'] as int,
      plateNumber: json['plate_number'] as String,
      paymentStatus: paymentStatusFromString(json['payment_status'] as String),
      invoiceDate: DateTime.parse(json['invoice_date'] as String),
    );
  }
}
