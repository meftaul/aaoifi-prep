export type TocEntry = [level: 1 | 2, id: string, title: string]

export interface GuideContent {
  toc: TocEntry[]
  html: string
}

export interface Guide {
  slug: string
  standard: string
  title: string
  arabic: string
  bangla: string
  summary: string
  meta: string[]
  load: () => Promise<GuideContent>
}

export const guides: Guide[] = [
  {
    slug: 'ss-02',
    standard: "AAOIFI Shari'ah Standard No. 2",
    title: 'Debit Card, Charge Card and Credit Card',
    arabic: 'المعيار الشرعي رقم (٢): بطاقة الحسم وبطاقة الائتمان',
    bangla: 'ডেবিট কার্ড, চার্জ কার্ড ও ক্রেডিট কার্ড — শরিয়াহ স্ট্যান্ডার্ড নং ২ এর পূর্ণাঙ্গ স্টাডি গাইড',
    summary:
      "A beginner-friendly academic guide to AAOIFI Shari'ah Standard No. (2): its rulings, Shari'ah evidence, juristic reasoning, International Islamic Fiqh Academy resolutions, the 2026 Bangladesh Bank Islamic Credit Card Guidelines, worked examples in BDT, case studies and practice questions — in English and Bangla.",
    meta: [
      "Source: AAOIFI Shari'ah Standard No. (2), issued 27 Safar 1421 AH / 31 May 2000 (pp. 71–82 of the Shari'ah Standards volume).",
      'Prepared: November 2026 · English & Bangla · For study purposes — not a fatwa.',
    ],
    load: () => import('./content/ss02.json').then((m) => m.default as GuideContent),
  },
  {
    slug: 'ss-03',
    standard: "AAOIFI Shari'ah Standard No. 3",
    title: 'Procrastinating Debtor',
    arabic: 'المعيار الشرعي رقم (٣): المدين المماطل',
    bangla: 'শরিয়াহ স্ট্যান্ডার্ড নং ৩: টালবাহানাকারী (সামর্থ্যবান অথচ পরিশোধে বিলম্বকারী) দেনাদার',
    summary:
      'A bilingual study guide to every clause of SS 3: what the standard says, the reasoning in its Appendix (B), how IIFA, regulators and Bangladesh banks deal with late payment, worked examples in BDT, case studies and practice questions.',
    meta: [
      "Source: Shari'ah Standard No. (3): Procrastinating Debtor (Revised Standard), AAOIFI Shari'ah Standards, pp. 85–101.",
      "Issued: 27 Safar 1421 AH / 31 May 2000 · Revised version adopted: Shari'ah Board meeting No. 38, 28 Sha'ban – 1 Ramadan 1435 AH / 26–28 June 2014.",
      'Compared with: IIFA Resolutions 51, 109, 133 · Bangladesh Bank (2009 Guidelines; 2026 Islamic Credit Card Guidelines) · SBP · BNM SAC.',
      "Prepared: November 2026 · This guide explains and compares; it is not a fatwa. For a ruling on a real case, consult your institution's Shari'ah Supervisory Committee or a qualified mufti.",
    ],
    load: () => import('./content/ss03.json').then((m) => m.default as GuideContent),
  },
]

export function guideHref(slug: string) {
  return `${import.meta.env.BASE_URL}?guide=${slug}`
}
