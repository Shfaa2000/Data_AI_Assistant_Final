# Data Quality Rules — Cloud Billing Dataset

## 1. AvailabilityZone Validity

- الفئة: Validity
- الدليل: قيم AvailabilityZone في صفوف Microsoft رقمية، وتتطابق في العينة مع قيم سعرية.
- التفسير: توجد مشكلة محتملة في mapping أو column alignment في العينة.
- الإجراء: استخدام AvailabilityZone_valid لتحديد القيم الرقمية غير الموثوقة.
- الحد: لا ننسب المشكلة إلى نظام Microsoft نفسه دون فحص الملف المصدر.

## 2. PricingQuantity Zero

- الفئة: Validity
- الدليل: توجد صفوف PricingQuantity فيها تساوي صفرًا، لكن BilledCost أو EffectiveCost لا يساوي صفرًا.
- التفسير: PricingQuantity وحدها لا تكفي لإثبات عدم وجود استخدام.
- الإجراء: فحص PricingUnit وChargeDescription قبل تفسير القيمة.

## 3. ChargeFrequency Consistency

- الفئة: Consistency
- الدليل: توجد صيغ مختلفة مثل Usage-Based وUsage-based وOne-Time.
- الإجراء: إنشاء ChargeFrequency_normalized مع الاحتفاظ بالقيمة الأصلية.

## 4. Tags Consistency

- الفئة: Consistency
- الدليل: انخفض عدد مفاتيح Tags من 354 إلى 30 بعد lowercase وstrip.
- التفسير: اختلاف case والمسافات كان يسبب تضخيم عدد المفاتيح.
- الإجراء: استخدام extract_normalized_tag_keys عند تحليل Tags.
- الحد: لا ندمج مفاتيح مختلفة دلاليًا مثل env وenvironment دون دليل.

## 5. Completely Empty Columns

- الفئة: Completeness
- الدليل: ChargeClass وCommitmentDiscountName فارغان في جميع صفوف العينة.
- التفسير: العمودان غير معبأين في هذه العينة.
- الإجراء: لا يُستخدمان في التحليل الحالي، ولا يُحذفان من المخطط.
- الحد: لا نصنفهما Not Applicable دون توثيق من مصدر البيانات.

## 6. Resource Completeness

- الفئة: Completeness
- الدليل: ResourceName مفقود بنسبة عالية، وResourceType مفقود جزئيًا.
- التفسير: مستوى تفصيل الموارد يختلف بين Providers.
- الإجراء: عدم الاعتماد على ResourceName وحده، واستخدام ResourceId عند توفره.

## 7. Date Column Types

- الفئة: Schema
- الدليل: أعمدة BillingPeriod وChargePeriod قُرئت كـobject.
- الأثر: لا يمكن إجراء تحليل زمني موثوق قبل تحويلها إلى datetime.
- الإجراء: تحويلها عند بدء مرحلة التحليل الزمني.
أعمدة التاريخ قُرئت من Raw CSV كنوع object، ثم تعامل معها BigQuery وفق Reference Schema كحقول زمنية صالحة للتحليل.

## 8. Identifier Types

- الفئة: Schema
- الدليل: BillingAccountId وSubAccountId مخزنان كنص.
- التفسير: هذا مناسب لأن المعرّفات لا تُستخدم في العمليات الحسابية.
- الإجراء: إبقاؤهما كنص.

## 9. Row Grain

- الفئة: Uniqueness
- الدليل: لا توجد صفوف متطابقة بالكامل في العينة.
- التفسير: الصف يمثل charge line item، وليس فاتورة كاملة.
- الإجراء: لا نعتبر تكرار المورد وحده Duplicate.

## 10. Repeated Resources

- الفئة: Uniqueness
- الدليل: قد يظهر ResourceId أكثر من مرة في ChargePeriods أو Charges مختلفة.
- التفسير: التكرار قد يكون طبيعيًا في بيانات الفوترة.
- الإجراء: يجب أن يشمل فحص التكرار الفترة وخصائص الـcharge.

## 11. Negative Costs

- الفئة: Business Rule
- الدليل: توجد 13 قيمة BilledCost سالبة: صف AWS Credit و12 صف Microsoft Usage.
- الإجراء: لا تُحذف القيم السالبة تلقائيًا.
- الحد: سبب صفوف Microsoft السالبة غير مثبت من العينة وحدها.

## 12. Zero Costs

- الفئة: Business Rule
- الدليل: توجد 329 قيمة BilledCost تساوي صفرًا.
- التفسير: الصفوف الصفرية ليست مجموعة متجانسة بالضرورة.
- الإجراء: فحص ProviderName وServiceCategory وChargeDescription قبل تفسيرها.
- الحد: Free Tier فرضية محتملة لبعض الصفوف، وليس تفسيرًا مؤكدًا لجميعها.

## 13. Outlier Detection

- الفئة: Methodology
- الدليل: IQR صنفت 222 صفًا، بينما Adjusted Boxplot صنفت قرابة 87 صفًا.
- التفسير: توزيع BilledCost ملتوي ومتركز قرب الصفر.
- الإجراء: استخدام العلامة للمراجعة فقط، وليس للحذف الآلي.
- الحد: قيمة medcouple مرتفعة جدًا، لذلك النتيجة تقريبية وليست حقيقة مطلقة.
قيمة medcouple قريبة جدًا من الحد الأعلى النظري، ولذلك يجب التعامل مع النتيجة كمؤشر للمراجعة، والتحقق لاحقًا من متانة التطبيق الإحصائي.


## 14. Schema Gate Before Staging

- الفئة: Pipeline Contract
- القاعدة: يجب أن تتطابق أسماء الأعمدة وترتيبها مع Reference Schema قبل التحميل.
- الإجراء: إيقاف التشغيل عند أي اختلاف.

## 15. Reconciliation Before Publishing

- الفئة: Pipeline Control
- القاعدة: لا يتم تحديث Published Table إلا بعد نجاح مقارنة المؤشرات الحرجة.
- الإجراء: إيقاف النشر والإبقاء على Published السابق عند الفشل.

## 16. Verified Evidence Only

- الفئة: Evidence Quality
- القاعدة: يتم تحديث latest.json فقط عندما تنجح جميع Reconciliation Checks.
- الإجراء: حفظ Evidence الفاشل للتدقيق دون استبدال آخر دليل موثوق.