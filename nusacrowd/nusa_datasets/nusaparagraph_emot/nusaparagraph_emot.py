from pathlib import Path
from typing import Dict, List, Tuple
import datasets
import pandas as pd
from nusacrowd.utils import schemas
from nusacrowd.utils.configs import NusantaraConfig
from nusacrowd.utils.constants import (DEFAULT_NUSANTARA_VIEW_NAME,
                                       DEFAULT_SOURCE_VIEW_NAME, Tasks)
_LOCAL = False
_DATASETNAME = "nusaparagraph_emot"
_SOURCE_VIEW_NAME = DEFAULT_SOURCE_VIEW_NAME
_UNIFIED_VIEW_NAME = DEFAULT_NUSANTARA_VIEW_NAME
_LANGUAGES = [
    "btk", "bew", "bug", "jav", "mad", "mak", "min", "mui", "rej", "sun"
]  # We follow ISO639-3 language code (https://iso639-3.sil.org/code_tables/639/data)
_CITATION = """\
@misc{winata2022nusax,
      title={NusaX: Multilingual Parallel Sentiment Dataset for 10 Indonesian Local Languages},
      author={Winata, Genta Indra and Aji, Alham Fikri and Cahyawijaya,
      Samuel and Mahendra, Rahmad and Koto, Fajri and Romadhony,
      Ade and Kurniawan, Kemal and Moeljadi, David and Prasojo,
      Radityo Eko and Fung, Pascale and Baldwin, Timothy and Lau,
      Jey Han and Sennrich, Rico and Ruder, Sebastian},
      year={2022},
      eprint={2205.15960},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
"""
_DESCRIPTION = """\
We introduce a novel high quality human curated corpora, i.e., NusaMenulis, which covers 12 languages spoken in Indonesia. The resource extend the coverage of languages to 5 new languages, i.e., Ambon (abs), Bima (bhp), Makassarese (mak), Palembang / Musi (mui), and Rejang (rej).
For the emotion recognition task, we cover the 6 basic emotions (Ekman, 1992): fear, disgusted, sad, happy, angry, and surprise, and an additional emotion label: shame (Poulson and of Tasmania. School of Management, 2000.
"""
_HOMEPAGE = "https://github.com/IndoNLP/nusa-writes/tree/main/data"
_LICENSE = "Creative Commons Attribution Share-Alike 4.0 International"
_SUPPORTED_TASKS = [Tasks.EMOTION_CLASSIFICATION]
_SOURCE_VERSION = "1.0.0"
_NUSANTARA_VERSION = "1.0.0"
_URLS = {
    "train":
    "https://raw.githubusercontent.com/IndoNLP/nusa-writes/main/data/nusa_alinea-emot-{lang}-train.csv",
    "validation":
    "https://raw.githubusercontent.com/IndoNLP/nusa-writes/main/data/nusa_alinea-emot-{lang}-valid.csv",
    "test":
    "https://raw.githubusercontent.com/IndoNLP/nusa-writes/main/data/nusa_alinea-emot-{lang}-test.csv",
}
def nusantara_config_constructor(lang, schema, version):
    """Construct NusantaraConfig with nusaparagraph_emot_{lang}_{schema} as the name format"""
    if schema != "source" and schema != "nusantara_text":
        raise ValueError(f"Invalid schema: {schema}")
    if lang == "":
        return NusantaraConfig(
            name="nusaparagraph_emot_{schema}".format(schema=schema),
            version=datasets.Version(version),
            description=
            "nusaparagraph_emot with {schema} schema for all 10 languages".
            format(schema=schema),
            schema=schema,
            subset_id="nusaparagraph_emot",
        )
    else:
        return NusantaraConfig(
            name="nusaparagraph_emot_{lang}_{schema}".format(lang=lang,
                                                             schema=schema),
            version=datasets.Version(version),
            description=
            "nusaparagraph_emot with {schema} schema for {lang} language".
            format(lang=lang, schema=schema),
            schema=schema,
            subset_id="nusaparagraph_emot",
        )
LANGUAGES_MAP = {
    "btk": "batak",
    "bew": "betawi",
    "bug": "buginese",
    "jav": "javanese",
    "mad": "madurese",
    "mak": "makassarese",
    "min": "minangkabau",
    "mui": "musi",
    "rej": "rejang",
    "sun": "sundanese"
}
class NusaParagraphEmot(datasets.GeneratorBasedBuilder):
    """NusaParagraph-Emot is a 7-labels (fear, disgusted, sad, happy, angry, surprise, and shame) emotion classification dataset for 10 Indonesian local languages."""
    BUILDER_CONFIGS = ([
        nusantara_config_constructor(lang, "source", _SOURCE_VERSION)
        for lang in LANGUAGES_MAP
    ] + [
        nusantara_config_constructor(lang, "nusantara_text",
                                     _NUSANTARA_VERSION)
        for lang in LANGUAGES_MAP
    ] + [
        nusantara_config_constructor("", "source", _SOURCE_VERSION),
        nusantara_config_constructor("", "nusantara_text", _NUSANTARA_VERSION)
    ])
    DEFAULT_CONFIG_NAME = "nusaparagraph_emot_ind_source"
    def _info(self) -> datasets.DatasetInfo:
        if self.config.schema == "source":
            features = datasets.Features({
                "id": datasets.Value("string"),
                "text": datasets.Value("string"),
                "label": datasets.Value("string"),
            })
        elif self.config.schema == "nusantara_text":
            features = schemas.text_features([
                "fear", "disgusted", "sad", "happy", "angry", "surprise",
                "shame"
            ])
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )
    def _split_generators(
            self, dl_manager: datasets.DownloadManager
    ) -> List[datasets.SplitGenerator]:
        """Returns SplitGenerators."""
        if self.config.name == "nusaparagraph_emot_source" or self.config.name == "nusaparagraph_emot_nusantara_text":
            # Load all 12 languages
            train_csv_path = dl_manager.download_and_extract([
                _URLS["train"].format(lang=lang)
                for lang in LANGUAGES_MAP
            ])
            validation_csv_path = dl_manager.download_and_extract([
                _URLS["validation"].format(lang=lang)
                for lang in LANGUAGES_MAP
            ])
            test_csv_path = dl_manager.download_and_extract([
                _URLS["test"].format(lang=lang)
                for lang in LANGUAGES_MAP
            ])
        else:
            lang = self.config.name[12:15]
            train_csv_path = Path(
                dl_manager.download_and_extract(
                    _URLS["train"].format(lang=lang)))
            validation_csv_path = Path(
                dl_manager.download_and_extract(
                    _URLS["validation"].format(lang=lang)))
            test_csv_path = Path(
                dl_manager.download_and_extract(
                    _URLS["test"].format(lang=lang)))
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": train_csv_path},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"filepath": validation_csv_path},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": test_csv_path},
            ),
        ]
    def _generate_examples(self, filepath: Path) -> Tuple[int, Dict]:
        if self.config.schema != "source" and self.config.schema != "nusantara_text":
            raise ValueError(f"Invalid config: {self.config.name}")
        if self.config.name == "nusaparagraph_emot_source" or self.config.name == "nusaparagraph_emot_nusantara_text":
            ldf = []
            for fp in filepath:
                ldf.append(pd.read_csv(fp))
            df = pd.concat(ldf, axis=0, ignore_index=True).reset_index()
            # Have to use index instead of id to avoid duplicated key
            df = df.drop(columns=["id"]).rename(columns={"index": "id"})
        else:
            df = pd.read_csv(filepath).reset_index()
        for row in df.itertuples():
            ex = {"id": str(row.id), "text": row.text, "label": row.label}
            yield row.id, ex