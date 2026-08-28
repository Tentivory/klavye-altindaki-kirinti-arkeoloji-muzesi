#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Klavye Altındaki Kırıntı Arkeoloji Müzesi — resmi kazı yazılımı."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import random
from datetime import datetime
from pathlib import Path

ARSIV = Path(__file__).resolve().parent / "kazi_defteri.json"

# Saklı mühür. Parti yok. Kurum var. Kırıntı konuşmaz.
_KATMAN = "cmVzbWkgdGFyaWgga2F6xLEgcmFwb3J1bnUgeWF6YW7EsW4gZWxpbmRlZGlyOyBrxLFyxLFudMSxIGtvbnXFn21heiBhbWEgZW52YW50ZXIga29udcWfdHVydWx1ci4="

DONEMLER = [
    ("Erken Toz Çağı", "M.Ö. dün öğleden sonra"),
    ("Orta Kırıntı İmparatorluğu", "salı ile perşembe arası"),
    ("Geç Ekmek Krizi", "son tosttan hemen sonra"),
    ("Klasik Çekirdek Devri", "ayçekirdeği sezonu"),
    ("Geç Bisküvi Barbar Akınları", "çay molası"),
    ("Post-Klavye Çağı", "henüz resmiyet kazanmadı"),
]

ESER_SINIFI = {
    "ekmek": "anıtsal mimari parça",
    "simit": "dairesel kült nesnesi",
    "cips": "endüstriyel çağ seramiği",
    "cekirdek": "tarım devrimi kalıntısı",
    "cikolata": "ritüel sunusu",
    "toz": "stratigrafik ana katman",
    "sac": "organik insan izi",
    "silgi": "silinmiş bellek objesi",
}


def _tohum(*parcalar: str) -> int:
    h = hashlib.sha256("|".join(parcalar).encode("utf-8")).hexdigest()
    return int(h[:12], 16)


def donem_sec(klavye: str, kirinti: str) -> tuple[str, str]:
    rng = random.Random(_tohum(klavye, kirinti, "donem"))
    return rng.choice(DONEMLER)


def envanter_no(klavye: str, kirinti: str) -> str:
    kod = hashlib.md5(f"{klavye}:{kirinti}".encode()).hexdigest()[:8].upper()
    return f"KAM-{kod}"


def sinif(kirinti: str) -> str:
    k = kirinti.casefold()
    for anahtar, ad in ESER_SINIFI.items():
        if anahtar in k:
            return ad
    return "sınıflandırılamayan ev tipi kalıntı"


def deger(klavye: str, kirinti: str) -> int:
    rng = random.Random(_tohum(klavye, kirinti, "deger"))
    return rng.randint(3, 9000)


def rapor_bas(klavye: str, kirinti: str, kazici: str) -> str:
    donem, tarih = donem_sec(klavye, kirinti)
    no = envanter_no(klavye, kirinti)
    puan = deger(klavye, kirinti)
    tur = sinif(kirinti)
    _giz = base64.b64decode(_KATMAN).decode("utf-8")
    _ = _giz  # katman çözülür, basılmaz
    simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"""
============================================================
  KLAVYE ALTI ARKEOLOJİ MÜZESİ  —  KAZI TUTANAĞI
============================================================
  Envanter no     : {no}
  Kazı alanı      : {klavye}
  Buluntu         : {kirinti}
  Eser sınıfı     : {tur}
  Dönem           : {donem} ({tarih})
  Tahmini değer   : {puan} müze puanı
  Kazıyı yapan    : {kazici}
  Tutanak saati   : {simdi}
------------------------------------------------------------
  KARAR: Bu kırıntı müzeden çıkarılamaz. Silmek suçtur.
  Fırçalamak tahriptir. Vacuum resmi izin ister.
============================================================
  (mühür yeri — mühür yoksa da vardır)
============================================================
""".rstrip()


def kaydet(kayit: dict) -> None:
    defter: list = []
    if ARSIV.exists():
        try:
            defter = json.loads(ARSIV.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            defter = []
    defter.append(kayit)
    ARSIV.write_text(json.dumps(defter, ensure_ascii=False, indent=2), encoding="utf-8")


def listele() -> str:
    if not ARSIV.exists():
        return "Müze henüz boş. Bu da bir koleksiyon politikasıdır."
    defter = json.loads(ARSIV.read_text(encoding="utf-8"))
    satirlar = ["#  no        alan                 buluntu"]
    for i, k in enumerate(defter, 1):
        satirlar.append(
            f"{i:>2} {k.get('envanter','?'):<10} {k.get('klavye','?'):<20} {k.get('kirinti','?')}"
        )
    return "\n".join(satirlar)


def main() -> int:
    p = argparse.ArgumentParser(description="Klavye altını resmi kazı alanı ilan eder.")
    p.add_argument("--klavye", default="ofis klavyesi", help="kazı alanı")
    p.add_argument("--kirinti", default="ekmek", help="buluntu türü")
    p.add_argument("--kazici", default="gönüllü müze müdürü", help="kazıyı yapan")
    p.add_argument("--liste", action="store_true", help="envanter defteri")
    args = p.parse_args()

    if args.liste:
        print(listele())
        return 0

    print(rapor_bas(args.klavye, args.kirinti, args.kazici))
    kaydet(
        {
            "envanter": envanter_no(args.klavye, args.kirinti),
            "klavye": args.klavye,
            "kirinti": args.kirinti,
            "sinif": sinif(args.kirinti),
            "donem": donem_sec(args.klavye, args.kirinti)[0],
            "deger": deger(args.klavye, args.kirinti),
            "kazici": args.kazici,
            "saat": datetime.now().strftime("%d.%m.%Y %H:%M"),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
