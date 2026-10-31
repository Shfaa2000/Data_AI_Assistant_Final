# Cloud and BigQuery Foundations

## 1. Training Environment

- Project Name: Data AI Assistant Training
- Project ID: data-ai-assistant-training
- Dataset: cloud_finops
- Reference Table: billing_cleaned
- Staging Table: billing_staging
- Published Table: billing_pipeline_day2
- Analytical View: v_service_costs
- BigQuery Location: US
- Billing Status: Billing disabled; BigQuery remained available within the accessible limits, while Cloud Storage bucket creation was unavailable.
- Authentication: Application Default Credentials using the Google user account.
- Object Storage Backend: Local content-addressed landing zone.

## 2. Goal

نقل بيانات Cloud Billing المنظفة من البيئة المحلية إلى BigQuery، وتشغيل تحليلات سحابية عليها، ثم مطابقة النتائج مع pandas وSQLite للتأكد من أن عملية النقل لم تغيّر عدد الصفوف أو القيم المالية.

## 3. GCP Resource Hierarchy

### Organization

تمثل الشركة أو الجهة المالكة لموارد Google Cloud.

في البيئة التدريبية الحالية:

- Organization: No Organization / Personal Training Account

### Folder

حاوية اختيارية لتنظيم عدة Projects حسب القسم أو البيئة أو الفريق.

في المشروع الحالي لم نستخدم Folder.

### Project

الحاوية الأساسية التي تجمع:

- الخدمات.
- الموارد.
- الصلاحيات.
- الاستهلاك.
- الفوترة.

المشروع الحالي:

- Project Name: Data AI Assistant Training
- Project ID: [ضعي Project ID هنا]

### Service Resources

الموارد المستخدمة داخل المشروع:

- BigQuery Service
- cloud_finops Dataset
- billing_cleaned Table

## 4. IAM Model

### Principal

هوية تطلب الوصول إلى أحد موارد Google Cloud.

الـPrincipal المستخدم اليوم:

- حساب Google الذي أنشأ المشروع.

### Permission

إجراء واحد يمكن تنفيذه على Resource، مثل:

- إنشاء جدول.
- قراءة جدول.
- تشغيل Query.
- عرض Dataset.

### Role

مجموعة من Permissions يتم منحها إلى Principal.

- Current role: [انسخي اسم الدور الظاهر أمام حسابك في IAM]

### Policy Binding

ربط بين:

Principal + Role + Resource

أي تحديد من يستطيع تنفيذ ماذا، وعلى أي Resource.

### Service Account

هوية غير بشرية تستخدمها التطبيقات والبرامج للوصول إلى خدمات Google Cloud.

لم ننشئ Service Account اليوم لأن رفع البيانات وتشغيل الاستعلامات تم يدويًا من خلال حساب المستخدم.

سيُستخدم Service Account مستقبلًا عندما يتصل Python ETL Pipeline بـBigQuery دون تدخل يدوي.

### Least Privilege

منح كل مستخدم أو تطبيق أقل عدد من الصلاحيات التي يحتاج إليها لإتمام مهمته.

مثال:

برنامج يحتاج قراءة البيانات فقط يجب ألا يحصل على صلاحية Owner أو صلاحية حذف الجداول.

## 5. Storage and Database Concepts

### Cloud Storage

Cloud Storage هو Object Storage يُستخدم لتخزين الملفات والـObjects، مثل:

- CSV
- JSON
- PDF
- Images
- Backups
- Logs

Cloud Storage مناسب ليكون Raw Landing Zone، لكنه ليس محرك SQL تحليليًا مثل BigQuery.

### BigQuery

BigQuery هو Managed Cloud Data Warehouse مخصص لتخزين وتحليل البيانات المنظمة باستخدام SQL.

يتكون التنظيم المستخدم في المشروع من:

Project → Dataset → Table

BigQuery يدير البنية التحتية المطلوبة لتنفيذ الاستعلامات، ويجب الانتباه إلى كمية البيانات التي يقرأها كل Query.

### SQLite

SQLite هي Embedded Relational Database محلية.

خصائصها في المشروع:

- مخزنة في ملف واحد.
- لا تحتاج Cloud Project.
- لا تحتاج IAM.
- مناسبة للعينة الحالية والتحليل المحلي.
- لا تقدم خصائص Data Warehouse سحابي مُدار مثل BigQuery.

## 6. Current Data Flow

### Current Training Flow

Raw CSV  
→ pandas Ingestion  
→ Validation  
→ Cleaning  
→ Cleaned CSV  
→ Local Object Landing Zone using SHA-256  
→ BigQuery Staging  
→ Reconciliation  
→ Published Table  
→ SQL Views and Analytics  
→ Trusted Evidence JSON  
→ FastAPI  
→ HTTP Client

### Future Cloud Flow

عند توفر Billing سيتم استبدال Local Object Storage بـGoogle Cloud Storage Bucket، مع بقاء مراحل Staging وValidation وPublishing وEvidence كما هي.

## 7. BigQuery Table

- Source file: data/processed/billing_cleaned.csv
- Dataset: cloud_finops
- Table: billing_cleaned
- Loaded row count: 1000
- BilledCost: Numeric type confirmed by successful SUM query
- EffectiveCost: Numeric type confirmed by successful SUM query
- Exact BilledCost type: [انسخي FLOAT64 أو NUMERIC من Schema]
- Exact EffectiveCost type: [انسخي FLOAT64 أو NUMERIC من Schema]
- BillingPeriodStart type: [انسخي النوع من Schema]
- BillingPeriodEnd type: [انسخي النوع من Schema]
- ChargePeriodStart type: [انسخي النوع من Schema]
- ChargePeriodEnd type: [انسخي النوع من Schema]

### Cleaning Columns Included

- ChargeFrequency_normalized
- AvailabilityZone_valid
- BilledCost_outlier_adjusted

## 8. Query Analysis

### Query 1 — Overall Reconciliation

#### Business Question

هل عدد الصفوف والمجاميع المالية وعدد القيم السالبة والصفرية في BigQuery مطابق للنسخة المحلية؟

#### Result

- Rows returned: 1
- TotalRows: 1000
- TotalBilledCost: 20.52022672899
- TotalEffectiveCost: 14.97651418586
- NegativeRows: 13
- ZeroRows: 329
- Bytes processed: [ضعي القيمة الظاهرة في BigQuery]

#### Fact

BigQuery يحتوي على 1000 صف، وإجمالي BilledCost وEffectiveCost وعدد الصفوف السالبة والصفرية مطابق للنتائج المحلية.

#### Interpretation

عملية رفع البيانات إلى BigQuery لم تغيّر عدد الصفوف أو القيم المالية الأساسية.

#### Limitation

المطابقة تثبت اتساق عملية النقل والحساب، لكنها لا تثبت أن جميع القيم الواردة من المصدر صحيحة من ناحية الأعمال.

---

### Query 2 — Provider Summary

#### Business Question

كيف تتوزع الصفوف والتكلفة بين AWS وMicrosoft وOracle؟

#### Result

| Provider | RowCount | TotalBilledCost | TotalEffectiveCost |
|---|---:|---:|---:|
| AWS | 942 | 18.006639 | 13.000000 |
| Microsoft | 51 | 1.976514 | 1.976514 |
| Oracle | 7 | 0.537074 | 0.000000 |

- Rows returned: 3
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- AWS يمثل 942 صفًا من أصل 1000، أي 94.2% من الصفوف.
- AWS يمثل قرابة 87.75% من إجمالي BilledCost.
- Microsoft يمثل قرابة 9.63% من إجمالي BilledCost.
- Oracle يمثل قرابة 2.62% من إجمالي BilledCost.

#### Interpretation

العينة منحازة بقوة نحو AWS من حيث عدد الصفوف والتكلفة، ولذلك ستكون معظم النتائج الإجمالية متأثرة بسلوك AWS.

#### Limitation

لا يمكن اعتبار مقارنة المزودين عادلة بالكامل لأن أحجام العينات مختلفة جدًا: AWS لديه 942 صفًا، بينما Oracle لديه سبعة صفوف فقط.

---

### Query 3 — Billed and Effective Cost Gap

#### Business Question

عند أي Provider تظهر أكبر فجوة بين BilledCost وEffectiveCost؟

#### Result

| Provider | TotalBilledCost | TotalEffectiveCost | Gap |
|---|---:|---:|---:|
| AWS | 18.006639 | 13.000000 | 5.006639 |
| Oracle | 0.537074 | 0.000000 | 0.537074 |
| Microsoft | 1.976514 | 1.976514 | 0.000000 |

- Rows returned: 3
- Total Gap: 5.54371254313
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- AWS لديه أكبر Gap بقيمة 5.006639.
- AWS يمثل قرابة 90.31% من الفجوة الإجمالية.
- Oracle لديه Gap بقيمة 0.537074.
- Microsoft لا يظهر لديه Gap في العينة.

#### Interpretation

تعريف EffectiveCost أو توفره يختلف بين المزودين داخل هذه العينة.

#### Hypothesis

قد ترتبط فجوة AWS بطريقة توزيع Commitment Discounts أو Savings Plans أو خصومات أخرى، لكن العينة الحالية لا تثبت السبب.

ثبات EffectiveCost على الصفر عند Oracle قد يكون ناتجًا عن عدم توفر Mapping مناسب لهذا الحقل، لكن سببه غير مثبت.

#### Confidence

- وجود الفجوة: ثقة عالية.
- سبب الفجوة: ثقة منخفضة.

#### Required Next Test

فحص CommitmentDiscountId وContractedCost وListCost، ثم الرجوع إلى تعريف الحقول في مصدر بيانات كل Provider.

---

### Query 4 — Negative Costs

#### Business Question

كيف تتوزع القيم السالبة حسب Provider وChargeCategory؟

#### Result

| Provider | ChargeCategory | NegativeRowCount | TotalNegativeCost |
|---|---|---:|---:|
| AWS | Credit | 1 | -2.613700 |
| Microsoft | Usage | 12 | -0.161971 |

- Rows returned: 2
- Total negative rows: 13
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- AWS لديه صف سالب واحد مصنف صراحة Credit.
- Microsoft لديه 12 صفًا سالبًا مصنفًا Usage.
- القيمة السالبة لدى AWS أكبر من مجموع القيم السالبة لدى Microsoft من حيث القيمة المطلقة.

#### Interpretation

القيم السالبة ليست نوعًا واحدًا، ولا يمكن تطبيق تفسير AWS على Microsoft.

#### Hypothesis

صفوف Microsoft قد تمثل تصحيحًا أو تسوية أو سلوك فوترة آخر.

#### Confidence

- وجود القيم السالبة وتصنيفها: ثقة عالية.
- سبب Microsoft: ثقة منخفضة.

#### Required Next Test

مراجعة ملف الفوترة الأصلي أو توثيق Microsoft المطابق للحقول المستخدمة في العينة.

---

### Query 5 — Zero-Cost Distribution

#### Business Question

أين تتركز الصفوف التي تساوي فيها BilledCost صفرًا؟

#### Result

| Provider | ServiceCategory | ZeroRowCount |
|---|---|---:|
| AWS | Compute | 210 |
| AWS | Networking | 59 |
| AWS | Storage | 23 |
| AWS | Other | 14 |
| AWS | Management and Governance | 9 |
| AWS | Databases | 8 |
| AWS | Integration | 3 |
| AWS | Identity | 1 |
| Oracle | Networking | 1 |
| Microsoft | Storage | 1 |

- Rows returned: 10
- Total zero rows: 329
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- 327 من أصل 329 صفًا صفريًا موجودة لدى AWS، أي قرابة 99.39%.
- AWS Compute يحتوي 210 صفوف صفرية.
- AWS Compute يمثل قرابة 63.83% من جميع الصفوف الصفرية.
- Microsoft وOracle لديهما صف صفري واحد لكل منهما.

#### Interpretation

ظاهرة BilledCost الصفرية مرتبطة بصورة أساسية بصفوف AWS، وخاصة Compute.

#### Hypothesis

بعض صفوف Compute قد ترتبط بـFree Tier أو بكميات صغيرة جدًا أو بطريقة تسجيل الاستخدام، لكن لا يمكن تعميم سبب واحد على جميع الصفوف.

#### Confidence

- مكان تركز الصفوف الصفرية: ثقة عالية.
- سبب القيم الصفرية: ثقة منخفضة إلى متوسطة.

#### Required Next Test

تحليل ChargeDescription وPricingQuantity وPricingUnit للصفوف الصفرية، ثم مقارنة النتائج بتوثيق AWS.

---

### Query 6 — Top Services

#### Business Question

ما الخدمات التي تحرك معظم BilledCost؟

#### Result

| Provider | ServiceName | RowCount | TotalBilledCost |
|---|---|---:|---:|
| AWS | Amazon Elastic Compute Cloud | 554 | 16.041693 |
| Microsoft | Azure Kubernetes Service | 1 | 1.580880 |
| AWS | Amazon Relational Database Service | 13 | 0.753227 |
| Oracle | COMPUTE | 5 | 0.536000 |
| Microsoft | Azure DB for MySQL | 1 | 0.370968 |
| AWS | Red Hat OpenShift Service on AWS | 1 | 0.342000 |
| AWS | Elastic Load Balancing | 97 | 0.313684 |
| AWS | AmazonCloudWatch | 63 | 0.220170 |
| Microsoft | Virtual Machines | 1 | 0.175681 |
| AWS | Amazon Virtual Private Cloud | 57 | 0.165540 |

- Rows returned: 10
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- EC2 هي أعلى خدمة من حيث BilledCost بقيمة 16.041693.
- EC2 تمثل قرابة 78.18% من إجمالي BilledCost لجميع المزودين.
- EC2 تمثل قرابة 89.09% من إجمالي BilledCost الخاص بـAWS.
- Azure Kubernetes Service ظهرت في صف واحد، لكنها ثاني أعلى خدمة تكلفة.

#### Interpretation

التكلفة شديدة التركّز في EC2، لذلك أي تحليل FinOps أو تحسين للتكلفة يجب أن يبدأ من مكونات EC2.

عدد الصفوف وحده لا يحدد أهمية الخدمة؛ Azure Kubernetes Service مثال على صف واحد بتكلفة مرتفعة.

#### Limitation

ServiceName وحده قد لا يجمع جميع التكاليف المرتبطة بالخدمة؛ تكاليف EBS المرتبطة بـEC2 قد تظهر تحت Storage أو وصف مختلف.

---

### Query 7 — Resource Completeness

#### Business Question

أي Provider يوفر أفضل اكتمال لحقول ResourceName وResourceType وResourceId؟

#### Result

| Provider | TotalRows | ResourceName | ResourceType | ResourceId |
|---|---:|---:|---:|---:|
| AWS | 942 | 0 | 151 | 867 |
| Microsoft | 51 | 51 | 51 | 51 |
| Oracle | 7 | 0 | 7 | 7 |

- Rows returned: 3
- Bytes processed: [ضعي القيمة الظاهرة]

#### Facts

- Microsoft لديه اكتمال 100% في الحقول الثلاثة ضمن 51 صفًا.
- AWS لا يحتوي ResourceName في العينة.
- AWS يحتوي ResourceType في 151 صفًا فقط، أي قرابة 16.03%.
- AWS يحتوي ResourceId في 867 صفًا، أي قرابة 92.04%.
- Oracle يحتوي ResourceType وResourceId في جميع صفوفه السبعة، لكنه لا يحتوي ResourceName.

#### Interpretation

Microsoft هو أفضل Provider في اكتمال الحقول الثلاثة معًا ضمن هذه العينة.

في AWS، ResourceId أكثر فائدة من ResourceName للتحليل على مستوى المورد.

#### Additional SQLite Evidence

- AWS لديه 799 ResourceId فريدًا مقابل 867 قيمة ResourceId غير فارغة.
- Microsoft لديه 36 ResourceId فريدًا مقابل 51 قيمة غير فارغة.
- Oracle لديه سبعة ResourceId فريدة مقابل سبعة صفوف.

هذا يثبت أن المورد نفسه قد يظهر في أكثر من Charge Line Item، وخاصة لدى AWS وMicrosoft.

#### Limitation

عينة Microsoft صغيرة مقارنة بـAWS، وعينة Oracle المكونة من سبعة صفوف غير كافية لتعميم جودة بيانات Oracle.

## 9. Reconciliation

| Metric | SQLite/pandas | BigQuery | Status |
|---|---:|---:|---|
| Total rows | 1000 | 1000 | PASS |
| Total BilledCost | 20.52022672899 | 20.52022672899 | PASS |
| Total EffectiveCost | 14.97651418586 | 14.97651418586 | PASS |
| Negative rows | 13 | 13 | PASS |
| Zero rows | 329 | 329 | PASS |
| AWS rows | 942 | 942 | PASS |
| Microsoft rows | 51 | 51 | PASS |
| Oracle rows | 7 | 7 | PASS |

### Reconciliation Conclusion

نقل البيانات من CSV المحلي إلى BigQuery لم يغيّر عدد الصفوف أو المجاميع المالية أو توزيع المزودين عند الدقة المعروضة.

هذا يثبت اتساق عملية النقل والتحليل بين البيئة المحلية وBigQuery، لكنه لا يثبت صحة جميع القيم التجارية الواردة من المصدر.

## 10. Main FinOps Insights

### Insight 1 — AWS يسيطر على العينة

- Fact: AWS يمثل 94.2% من الصفوف وقرابة 87.75% من BilledCost.
- Interpretation: معظم مؤشرات العينة الإجمالية تتأثر بسلوك AWS.
- Limitation: النتائج لا تمثل توزيعًا متوازنًا بين المزودين.

### Insight 2 — EC2 هو المحرك الأساسي للتكلفة

- Fact: EC2 يمثل قرابة 78.18% من إجمالي BilledCost.
- Interpretation: تحليل EC2 ومكوناته المرتبطة يجب أن يكون أولوية FinOps.
- Limitation: بعض تكاليف EC2 قد تظهر تحت Storage بسبب EBS.

### Insight 3 — Gap لا يساوي Discount مثبتًا

- Fact: AWS لديه Gap يساوي 5.006639.
- Interpretation: BilledCost وEffectiveCost لا يمثلان القيمة نفسها في صفوف AWS.
- Limitation: لا يمكن إثبات أن كامل Gap ناتج عن Savings Plans أو Commitment Discounts دون اختبار إضافي.

### Insight 4 — الصفوف الصفرية مركزة في AWS Compute

- Fact: AWS Compute يحتوي 210 من أصل 329 صفًا صفريًا.
- Interpretation: ظاهرة التكلفة الصفرية ليست موزعة بالتساوي بين المزودين والخدمات.
- Limitation: Free Tier فرضية محتملة وليست تفسيرًا مثبتًا لجميع الصفوف.

### Insight 5 — تصنيف السالب يختلف بين المزودين

- Fact: AWS السالب مصنف Credit، بينما Microsoft السالب مصنف Usage.
- Interpretation: لا يمكن دمج جميع القيم السالبة تحت معنى واحد.
- Limitation: سبب Microsoft يحتاج إلى مصدر فوترة أو توثيق إضافي.

### Insight 6 — Resource Completeness يختلف حسب Provider

- Fact: Microsoft مكتمل في ResourceName وResourceType وResourceId، بينما AWS يعتمد بصورة أساسية على ResourceId.
- Interpretation: تحليل Resource-level يجب أن يستخدم أعمدة مختلفة حسب Provider.
- Limitation: اختلاف حجم العينات يمنع المقارنة المطلقة بين جودة المزودين.

## 11. Cost Awareness

- Maximum bytes billed: 10 MB / 10485760 bytes
- Actual bytes processed per query: [لم تظهر في النتائج المرسلة — أضيفيها إن كنت سجلتها]

### Why SELECT * Should Be Avoided

BigQuery يعالج البيانات بحسب الأعمدة والصفوف التي يحتاج إليها الاستعلام.

استخدام SELECT * قد يقرأ أعمدة لا نحتاج إليها، مما يزيد كمية البيانات المعالجة والتكلفة ووقت التنفيذ.

الأفضل اختيار الأعمدة المطلوبة فقط.

## 12. Current Limitations

- البيانات Synthetic وتتكون من 1000 صف فقط.
- توزيع المزودين غير متوازن.
- البيانات لا تدعم Monthly Trend حقيقيًا بسبب محدودية الفترات.
- لم يتم إنشاء Service Account؛ الاتصال الحالي يعتمد على User ADC.
- Cloud Storage Bucket غير متاح بسبب تعطيل Billing وعدم توفر وسيلة دفع مناسبة.
- تم تنفيذ Local Object Storage كبديل، وليس تخزينًا سحابيًا فعليًا.
- Reconciliation الحالية تعتمد على مؤشرات مجمعة ولا تثبت التطابق صفًا بصف.
- أسباب Microsoft Negative Usage وAWS Billed/Effective Gap لم تثبت نهائيًا.
- Evidence يصف البيانات المحملة فقط ولا يقدم Forecasting أو Root-Cause نهائيًا.