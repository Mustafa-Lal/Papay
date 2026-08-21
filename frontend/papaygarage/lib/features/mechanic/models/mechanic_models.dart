class MechanicCustomer {
  final int id;
  final String? customerName;
  final String? phoneNumber;
  final String? qid;

  MechanicCustomer({
    required this.id,
    this.customerName,
    this.phoneNumber,
    this.qid,
  });

  factory MechanicCustomer.fromJson(Map<String, dynamic> json) {
    return MechanicCustomer(
      id: json['id'],
      customerName: json['customer_name'],
      phoneNumber: json['phone_number'],
      qid: json['qid'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        if (customerName != null) 'customer_name': customerName,
        if (phoneNumber != null) 'phone_number': phoneNumber,
        if (qid != null) 'qid': qid,
      };
}

class MechanicItem {
  final int id;
  final int invoiceId;
  final String description;
  final int quantity;
  final double unitPrice;
  final double commission;

  MechanicItem({
    required this.id,
    required this.invoiceId,
    required this.description,
    required this.quantity,
    required this.unitPrice,
    required this.commission,
  });

  factory MechanicItem.fromJson(Map<String, dynamic> json) {
    return MechanicItem(
      id: json['id'],
      invoiceId: json['invoice_id'],
      description: json['description'],
      quantity: double.parse(json['quantity'].toString()).toInt(),
      unitPrice: double.parse(json['unit_price'].toString()),
      commission: double.parse(json['commission'].toString()),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'invoice_id': invoiceId,
        'description': description,
        'quantity': quantity,
        'unit_price': unitPrice,
        'commission': commission,
      };

  double get total => (quantity * unitPrice) + commission;
}

enum PaymentStatus { paid, unpaid, partiallyPaid }

PaymentStatus parsePaymentStatus(String status) {
  switch (status.toUpperCase()) {
    case 'PAID':
      return PaymentStatus.paid;
    case 'UNPAID':
      return PaymentStatus.unpaid;
    case 'PARTIALLY_PAID':
      return PaymentStatus.partiallyPaid;
    default:
      return PaymentStatus.unpaid;
  }
}

String paymentStatusLabel(PaymentStatus status) {
  switch (status) {
    case PaymentStatus.paid:
      return 'PAID';
    case PaymentStatus.unpaid:
      return 'UNPAID';
    case PaymentStatus.partiallyPaid:
      return 'PARTIALLY PAID';
  }
}

class MechanicInvoice {
  final int id;
  final String plateNumber;
  final double laborCharges;
  final PaymentStatus paymentStatus;
  final DateTime invoiceDate;
  final int createdBy;
  final MechanicCustomer customer;
  final List<MechanicItem> items;

  MechanicInvoice({
    required this.id,
    required this.plateNumber,
    required this.laborCharges,
    required this.paymentStatus,
    required this.invoiceDate,
    required this.createdBy,
    required this.customer,
    required this.items,
  });

  factory MechanicInvoice.fromJson(Map<String, dynamic> json) {
    return MechanicInvoice(
      id: json['id'],
      plateNumber: json['plate_number'],
      laborCharges: double.parse(json['labor_charges'].toString()),
      paymentStatus: parsePaymentStatus(json['payment_status']),
      invoiceDate: DateTime.parse(json['created_at'] ?? json['invoice_date']),
      createdBy: json['created_by'],
      customer: MechanicCustomer.fromJson(json['customer']),
      items: (json['items'] as List).map((i) => MechanicItem.fromJson(i)).toList(),
    );
  }

  double get subtotal => items.fold(0.0, (sum, item) => sum + item.total);
  double get grandTotal => subtotal + laborCharges;

  MechanicInvoice copyWith({
    int? id,
    String? plateNumber,
    double? laborCharges,
    PaymentStatus? paymentStatus,
    DateTime? invoiceDate,
    int? createdBy,
    MechanicCustomer? customer,
    List<MechanicItem>? items,
  }) {
    return MechanicInvoice(
      id: id ?? this.id,
      plateNumber: plateNumber ?? this.plateNumber,
      laborCharges: laborCharges ?? this.laborCharges,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      invoiceDate: invoiceDate ?? this.invoiceDate,
      createdBy: createdBy ?? this.createdBy,
      customer: customer ?? this.customer,
      items: items ?? this.items,
    );
  }
}

class MechanicInvoiceSummary {
  final int invoiceId;
  final String? name;
  final String plateNumber;
  final PaymentStatus paymentStatus;
  final DateTime invoiceDate;

  MechanicInvoiceSummary({
    required this.invoiceId,
    this.name,
    required this.plateNumber,
    required this.paymentStatus,
    required this.invoiceDate,
  });

  factory MechanicInvoiceSummary.fromJson(Map<String, dynamic> json) {
    return MechanicInvoiceSummary(
      invoiceId: json['invoice_id'],
      name: json['name'],
      plateNumber: json['plate_number'],
      paymentStatus: parsePaymentStatus(json['payment_status']),
      invoiceDate: DateTime.parse(json['invoice_date']),
    );
  }
}
