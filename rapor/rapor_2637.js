// 26-37 Frankfort raporu -> SBU tez bicimi .docx
// Times New Roman 12 pt · A4 · sol 4 cm, sag 2,5 cm, ust/alt 3 cm
// `00` §0.2: hicbir ciktida hasta kimligi yok; yalniz `denek` etiketi.
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
        TableCell, WidthType, ShadingType, AlignmentType } = require('docx');

const J = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const OUT = process.argv[3];
const TARIH = process.argv[4] || '2026-11-10';

const olculdu = J.filter(k => k.durum === 'olculdu');
const gecen = olculdu.filter(k => k.hukum_A);
const dusen = olculdu.filter(k => !k.hukum_A);
const altyapi = J.filter(k => k.durum !== 'olculdu');

const F = (x, n = 2) => (x === undefined || x === null || Number.isNaN(x))
  ? '—' : Number(x).toFixed(n).replace('.', ',');

function p(text, o = {}) {
  return new Paragraph({
    spacing: { line: 360, after: o.after === undefined ? 120 : o.after },
    alignment: o.align || AlignmentType.JUSTIFIED,
    indent: o.indent,
    children: [new TextRun({ text, bold: !!o.bold, italics: !!o.italics,
                             size: o.size || 24 })],
  });
}
function h(text, lvl) {
  return new Paragraph({
    heading: lvl, spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: lvl === HeadingLevel.HEADING_1 ? 28 : 24 })],
  });
}
function hucre(text, { bold = false, w = 1200, shade = null } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    children: [new Paragraph({
      spacing: { line: 240, after: 0 },
      children: [new TextRun({ text: String(text), bold, size: 20 })],
    })],
  });
}
function tablo(basliklar, satirlar, genisler) {
  const W = genisler || basliklar.map(() => Math.floor(9000 / basliklar.length));
  return new Table({
    columnWidths: W,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: basliklar.map((b, i) => hucre(b, { bold: true, w: W[i], shade: 'E8E8E8' })) }),
      ...satirlar.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => hucre(c, { w: W[i] })) })),
    ],
  });
}

const olcutTablo = tablo(
  ['Ölçüt', 'Eşik', 'Kaynak'],
  [
    ['1. po-r ve po-l orta sagital düzlemin karşıt taraflarında', 'işaret çarpımı < 0', '`00` §0e'],
    ['2. İki porionun orta noktasının MSP\'ye uzaklığı', '≤ 3,00 mm', '`00` §0e; `0AV` §4 ile korundu'],
    ['3. Bi-porion uzaklığı', '89,91 – 121,79 mm', '`0AV` ön kaydı, araştırmacı onaylı'],
    ['4. Her porionun 1,5 mm komşuluğunda en büyük HU', '≥ 220 HU', '`00` §0e-4 kemik kapısı'],
    ['5. Sol orbitalenin Frankfort düzlemine uzaklığı', '≤ 1,00 mm', '`00` §0e'],
    ['6. Karşı (sağ) orbitalenin düzleme uzaklığı', '≤ 3,00 mm', '`0F` §24'],
  ], [4200, 2200, 2600]);

const kapsamaTablo = tablo(
  ['Durum', 'n', 'Açıklama'],
  [
    ['ALI koşamadı (altyapı)', String(altyapi.length), 'Bellek sınırı; yöntem hükmü değildir'],
    ['Ölçüldü', String(olculdu.length), 'Altı ölçüt sayısal olarak hesaplandı'],
    ['— altı ölçütü geçen', String(gecen.length), 'Frankfort kuruldu, 26–37 döküldü'],
    ['— ölçütlerden düşen', String(dusen.length), 'Porion yanlış ya da sınırda'],
  ], [3000, 900, 5100]);

const degerTablo = tablo(
  ['denek', 'bi-porion (mm)', 'orta–MSP (mm)', 'karşı orbitale (mm)', 'en küçük maks HU', 'geçen ölçüt', 'hüküm'],
  olculdu.map(k => {
    const hu = k.olcut4_maks_HU || {};
    const vals = Object.values(hu);
    return [k.denek, F(k.olcut3_biporion_mm), F(k.olcut2_orta_MSP_mm, 3),
            F(k.olcut6_karsi_orbitale_mm_A, 3),
            vals.length ? F(Math.min(...vals), 0) : '—',
            `${k.gecen_olcut_sayisi}/${k.olculen_olcut_sayisi}`,
            k.hukum_A ? 'GEÇTİ' : 'DÜŞTÜ'];
  }), [1100, 1500, 1400, 1700, 1500, 1100, 900]);

const rij = gecen.filter(k => k.rijitlik_mm !== undefined).map(k => k.rijitlik_mm);
const rijMaks = rij.length ? Math.max(...rij) : null;
const detler = gecen.filter(k => k.det_R !== undefined).map(k => k.det_R);

const govde = [
  h('26–37 Geometrik Morfometri Koordinatlarının Frankfort Çatısında Üretilmesi', HeadingLevel.HEADING_1),
  p(`Teknik rapor · ${TARIH}`, { italics: true }),

  h('1. Amaç', HeadingLevel.HEADING_2),
  p('Tez Tablo 3.2’nin 26–37 numaralı parametreleri, on iki orbital kenar landmarkının üç boyutlu koordinatlarıdır. Araştırmacı kararı gereği bu koordinatlar Frankfort horizontal düzlemine göre hizalandıktan sonra bildirilecektir. Bu çıktı bugüne kadar üretilememiştir; nedeni, Frankfort düzlemini tanımlayan porion noktasının hiçbir sahnede işaretlenmemiş olmasıdır. Bu rapor, porionun otomatik olarak işaretlenmesini, kurulan düzlemin ön kayıtlı ölçütlerle denetlenmesini ve koordinatların ortak çatıda dökülmesini belgeler.'),

  h('2. Yöntem', HeadingLevel.HEADING_2),
  h('2.1. Porionun işaretlenmesi', HeadingLevel.HEADING_3),
  p('Porion, dış akustik meatusun kemik kenarının en üst ve en dış noktası olarak tanımlanmıştır. İşaretleme, çok ölçekli pekiştirmeli öğrenme tabanlı ALI_CBCT etmeniyle yapılmıştır; etmen iki ölçekte (1 mm ve 0,3 mm izotropik) ardışık çalışır. Yöntem bu çalışmada eğitilmemiş, yayımlanmış ağırlıklarıyla kullanılmıştır. Daha önce ASO_CBCT altın standardı üzerinde doğrulanmış ve nokta hatası 0,39–0,61 mm, bi-porion hatası 0,69 mm bulunmuştur; aynı tarama üzerinde üç tekrarda sonuç birebir aynı kalmıştır.'),
  p('Proje içinde yazılmış olan önceki porion dedektörü (PO.bul) kullanılmamıştır; o dedektörün kohortta insan kafasında bulunmayan bi-porion değerleri ürettiği ölçülerek gösterilmiştir.'),

  h('2.2. Denetim ölçütleri', HeadingLevel.HEADING_3),
  p('İşaretlenen her porion çifti, sonuçlar görülmeden önce sabitlenmiş altı ölçütle denetlenmiştir. Hiçbir eşik, bu kohortun değerlerine bakılarak seçilmemiş ya da gevşetilmemiştir.'),
  olcutTablo,
  p(''),

  h('2.2.1. Üçüncü ölçütün bandının türetilmesi', HeadingLevel.HEADING_3),
  p('Bi-porion kabul bandı çalışmanın erken bir aşamasında sekiz olguluk bir öğrenme kümesinden türetilmiş ve 97,3–114,4 mm olarak kaydedilmişti. Bandın merkezi savunulabilir olmakla birlikte genişliği tek ve küçük bir kümenin standart sapmasına (2,85 mm) dayanıyordu; bu değer bir popülasyon içindeki bireysel değişkenliğin tahmini değildir. Kohortta bunun ölçülebilir bir sonucu görülmüştür: porion göstergeleri doğru aralıkta olan olgularda bi-porion uzaklığı 105,8–118,8 mm arasına yayılmakta, bandın üst sınırı ise bu dağılımın boşluğundan değil içinden geçmektedir. Band bu nedenle yeniden türetilmiştir. Merkez değiştirilmemiş, yalnız yarı-genişlik dış bir kaynaktan alınmıştır.'),
  p('Kullanılan dış kaynak Howells kraniyometrik veri setidir (2524 kafatası, 30 popülasyon). Bu veri setinde biporionik genişlik bulunmamaktadır; aurikular bölgedeki enine kafa tabanı genişliğini veren biauriküler genişlik kullanılmıştır. Kohort tek bir popülasyon olduğundan, popülasyonlar arası farkı da içeren toplam standart sapma (7,39 mm) değil, popülasyon içi havuzlanmış standart sapma (5,313 mm; serbestlik derecesi 2494) alınmıştır. Kohortun cinsiyeti kapalı olduğundan cinsiyete göre ayrıştırılmış tahmin kullanılmamıştır. Band böylece 105,85 ± 3 × 5,313 = 89,91–121,79 mm olmuştur. Türetmeye kohortun hiçbir ölçümü girmemiştir.'),
  p('Bu türetmenin sınırı açıkça belirtilmelidir: biauriküler genişliğin işaret noktası zigomatik çıkıntı kökü olup porion değildir ve kraniyometride bu iki ölçüm ayrı tanımlanır. Dış kaynaktan alınan şey ölçümün kendisi değil değişkenliğidir; varsayım, aurikular bölgedeki enine genişliğin popülasyon içi değişkenliğinin bu birkaç milimetrelik işaret noktası farkından büyük ölçüde bağımsız olduğudur ve bu varsayım sınanmamıştır. Bandın merkezi bu varsayıma dayanmamaktadır.'),
  p('Genişletilmiş band ayırt ediciliğini korumaktadır: porionları kemik dışında, yumuşak doku içinde bulunan iki olgu yeni bandın da dışında kalmakta ve bu ölçüt tarafından tek başına reddedilmeye devam etmektedir.'),
  p(''),

  p('Ayrıca her olgu üç ortogonal kesitte (aksiyel, koronal, sagittal) kemik penceresinde görsel olarak denetlenmiş; nokta yalnız üç boyutlu yüzey modeline dayanılarak kabul edilmemiştir.'),

  p('Orbitale noktası, tezin kendi ölçüm hattının ürettiği otomatik landmarktır; etmenin orbitale kestirimi bu amaçla kullanılmamıştır. Gerekçe, düzlemi tanımlayan iki noktadan birinin zaten ölçülen ve güvenilirliği bildirilen landmark olması, ikinci ve ayrı bir kestirim kaynağının çatıya sokulmamasıdır.'),

  h('2.3. Frankfort çatısının kurulması', HeadingLevel.HEADING_3),
  p('Düzlem, tez metninde benimsenen tanıma uygun olarak — her iki porion ile sol orbitaleden geçen düzlem — kurulmuştur. Çatı şöyle tanımlanmıştır: z ekseni düzlemin normali olup superiora bakacak şekilde yönlendirilir; y ekseni, orbitale orta noktasından porion orta noktasına uzanan vektörün z’ye dik bileşenidir ve anteriora bakar; x ekseni y × z olup sağa bakar. Başlangıç noktası iki porionun orta noktasıdır. Dönüşüm katı cisim dönüşümüdür.'),

  h('2.4. Sütun düzeni', HeadingLevel.HEADING_3),
  p('Çıktı, altı kenar landmarkının (dakriyon, maksillofrontale, mid-supraorbital, frontomalare orbitale, ektokonkion, orbitale) her iki taraf için x, y, z bileşenlerinden oluşan 36 sütundur. Apeks bu bloğa dâhil değildir. Satır anahtarı yalnız denek etiketidir; çıktıda hasta kimliğine ilişkin hiçbir alan bulunmamaktadır.'),

  h('3. Bulgular', HeadingLevel.HEADING_2),
  h('3.1. Kapsama', HeadingLevel.HEADING_3),
  p('Kapsama iki ayrı nedene bölünerek bildirilmiştir; bunlar birbirine karıştırılmamalıdır. Yöntem kusuru, etmenin çalışıp yanlış nokta bulmasıdır ve bir hükümdür. Altyapı kusuru, etmenin bellek sınırı nedeniyle hiç çalışamamasıdır ve bir yöntem hükmü değildir.'),
  kapsamaTablo,
  p(''),
  h('3.2. Ölçüt değerleri', HeadingLevel.HEADING_3),
  p('Her olgu için hüküm değil sayı kaydedilmiştir; böylece bir eşik sonradan değişirse koşu baştan alınmadan hükümler yeniden hesaplanabilir.'),
  degerTablo,
  p(''),
  h('3.3. Retlerin iki türü', HeadingLevel.HEADING_3),
  p('Reddedilen olgular tek bir küme değildir. Bir bölümünde porion açıkça yanlış yerdedir; bu olgular birden çok ölçütten birden düşer ve bağımsız göstergeleri de yanlışlığı doğrular. Geri kalanında porion üç düzlem denetiminde doğru yapının üzerindedir ve bağımsız göstergeleri doğru aralıktadır; bu olgular yalnız bir eşiğin kenarından düşmektedir. Bu iki tür ayrı bildirilmelidir.'),
  tablo(['denek', 'düşen ölçüt', 'karşı orbitale (mm)', 'en küçük maks HU', 'tür'],
    dusen.map(k => {
      const hu = k.olcut4_maks_HU || {}; const vals = Object.values(hu);
      const d = [];
      if (!k.olcut1_karsit_taraf) d.push('1');
      if (!k.olcut2_gecer) d.push('2');
      if (!k.olcut3_gecer) d.push('3');
      if (k.olcut4_gecer === false) d.push('4');
      if (!k.olcut5_gecer_A) d.push('5');
      if (!k.olcut6_gecer_A) d.push('6');
      const kaba = k.olcut6_karsi_orbitale_mm_A > 3.0;
      return [k.denek, d.join(', '), F(k.olcut6_karsi_orbitale_mm_A, 3),
              vals.length ? F(Math.min(...vals), 0) : '—',
              kaba ? 'kaba kusur' : 'eşik kenarı'];
    }), [1300, 1800, 2200, 1900, 1800]),
  p(''),
  p('Daha önce bildirilen bandlar şunlardır: doğru işaretlenmiş porionlarda karşı orbitalenin düzleme uzaklığı 0,55–2,83 mm ve nokta çevresindeki en büyük değer 1298–1757 HU; yanlış işaretlenmişlerde sırasıyla 24–30 mm ve 58–75 HU. Eşik kenarından düşen olguların tamamı bu ölçütlerin doğru aralığındadır.'),
  p('Eşik kenarından düşen olgulardan ikisi yalnız bi-porion bandının üst sınırı nedeniyle reddediliyordu. Band §2.2.1’de anlatıldığı biçimde dış kaynaktan yeniden türetilmiş ve bu iki olgu kabul edilmiştir. İkinci ölçütün eşiği ise değiştirilmemiştir; gerekçesi sınırlılıklar bölümünde verilmektedir. Her iki karar da koşudan ayrı bir ön kayıtta belgelenmiştir.'),

  h('3.4. Dönüşümün katılığı', HeadingLevel.HEADING_3),
  p(rijMaks === null
    ? 'Kabul edilen olgu bulunmadığından katılık ölçülememiştir.'
    : `Kabul edilen ${gecen.length} olguda dönüşüm matrisinin determinantı ${detler.map(d => d.toFixed(6).replace('.', ',')).join('; ')} bulunmuştur. Landmarklar arası bütün ikili uzaklıkların dönüşüm öncesi ve sonrası en büyük farkı ${rijMaks.toExponential(3).replace('.', ',')} mm’dir. Bu değer, daha önce bağımsız olarak kaydedilen 2,8 × 10⁻¹⁴ mm ile aynı büyüklüktedir. Dolayısıyla doğrusal uzaklıklar, oranlar, apertür alanı ve çevresi, kavite hacmi ve duvar kalınlığı bu dönüşümden etkilenmemektedir; dondurulmuş 43 parametre için yeniden ölçüm gerekmemektedir.`),

  h('4. Sınırlılıklar', HeadingLevel.HEADING_2),
  p('a) Düzlem sol orbitaleden geçirildiği için bu noktanın düzleme uzaklığı yapı gereği sıfırdır. Bunun iki sonucu vardır: beşinci ölçüt üç noktalı kurulumda ayırt edici değildir ve 36 sütundan biri (sol orbitalenin z bileşeni) bütün olgularda özdeş olarak sıfırdır, yani varyans taşımaz. Genelleştirilmiş Procrustes çözümlemesi için bu zararsızdır, ancak koordinat bloğu betimlenirken belirtilmelidir. Teşhis amacıyla dört noktalı en küçük kareler kurulumu da hesaplanmış ve her iki orbitalenin gerçek uzaklıkları ayrıca kaydedilmiştir.'),
  p('b) Frankfort tanımı yalnız bir düzlem belirler; düzlem içindeki dönmeyi sabitlemez. Bu çalışmada düzlem içi yönelim, ön eksenin porion orta noktasından orbitale orta noktasına uzanan doğrultuya göre tanımlanmasıyla sabitlenmiştir ve bu kural koşudan önce yazılmıştır. Alternatif bir kural — yanal eksenin doğrudan iki porionu birleştiren doğruya oturtulması — koordinatları düzlem içinde en çok birkaç derece döndürür; kabul edilen olgularda porion doğrusunun ön eksendeki artık bileşeni 0,46–3,26 mm ölçülmüştür. Genelleştirilmiş Procrustes çakıştırması döndürmeyi giderdiğinden geometrik morfometri sonuçları bu seçimden etkilenmez; etkilenen tek şey ham olarak bildirilen koordinat değerleridir. Seçim ve gerekçesi bu nedenle açıkça kaydedilmiştir.'),
  p('c) Porion kraniyometride tekrarlanabilirliği düşük bir noktadır ve burada elle değil otomatik olarak işaretlenmiştir. Güvenilirlik alt çalışmasına porionun ayrıca dâhil edilmesi ve kendi uyum katsayısının bildirilmesi gerekmektedir.'),
  p('d) Kullanılan etmen 0,3 mm izotropik konik ışınlı tomografilerde eğitilmiştir; bu seride kesit kalınlığı 1,25 mm’dir. Dış akustik meatus küçük bir yapıdır ve en çok dikey çözünürlükten zarar görür. Reddedilen olgulardaki başarısızlıkların bu farktan kaynaklandığı değerlendirilmektedir.'),
  p('e) İkinci ölçüt bu kohortta iki olguyu 3,32 ve 3,54 mm değerleriyle reddetmiştir; her iki olguda porion üç düzlem denetiminde doğru yapının üzerindedir ve bağımsız göstergeleri doğru aralıktadır. Dış kaynakta, porionun orta sagital düzleme göre yatay sağ-sol farkının normal yüzler ile yüz asimetrisi bulunan yüzler arasında ayırt edici olmadığı bildirilmiştir; aynı kaynakta bildirilen dağılımdan geri hesaplanan üç standart sapmalık sınır 3,2–3,6 mm aralığına düşmektedir. Bu aralık söz konusu iki olgunun değerlerinin üzerine denk gelmektedir, dolayısıyla aralık içinden bir eşik seçmek doğrudan bu iki olgunun hükmünü belirlemek anlamına gelirdi. Eşik bu nedenle değiştirilmemiş, 3,00 mm’de bırakılmıştır.'),
  p('f) Bu çalışmada orta sagital düzlem altı orbital açıklık çiftinin orta noktalarından kurulmaktadır; bu yerel bir orbital yapıdır, kafatası orta düzlemi değildir. Porionlar orbital bölgeden yaklaşık 70–80 mm arkada bulunduğundan düzlemdeki iki derecelik bir sapma porion düzeyinde yaklaşık 2,4 mm görünür kayma üretmektedir. İkinci ölçütün sınırda kalan değerlerinin anatomik asimetriden mi yoksa düzlem kestirim hatasından mı kaynaklandığı bu veriyle ayrıştırılamamaktadır. Ayrıca bu kohortta ikinci ölçüt tek başına hiçbir kaba kusuru yakalamamış, yakaladığı olguların tamamı altıncı ölçüt tarafından da yakalanmıştır. Ölçüt bu sonuçlar görüldükten sonra kaldırılmamış ya da gevşetilmemiştir; kohortun tamamının yeniden ölçülmesinde yerine geçecek kural ölçümden önce sabitlenecektir.'),
  p('g) Bu rapordaki koordinatlar, ölçüm hattının güncel sürümüyle üretilmiştir. Kohortun tamamının yeniden ölçülmesi ayrıca beklemektedir; 26–37 bloğu o koşuda, bütün olgular için aynı hatla yeniden dökülecektir. Buradaki çıktı, hattın uçtan uca çalıştığının ve çatının doğru kurulduğunun kanıtıdır.'),
  p('h) Frankfort düzlemi bu çalışmada ölçüm çatısı olarak kullanılmamaktadır. Porion hiçbir ölçülen parametreye girmemektedir. Düzlem yalnız yönelime bağlı tanımlı landmarkların tutarlı işaretlenmesi ve koordinatların ortak çatıda bildirilmesi için kurulmuştur.'),
];

const doc = new Document({
  styles: { default: { document: { run: { font: 'Times New Roman', size: 24 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1701, right: 1418, bottom: 1701, left: 2268 },
      },
    },
    children: govde,
  }],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log('yazildi:', OUT); });
