BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "audit_trail" (
	"record_uuid"	TEXT,
	"filepath"	TEXT,
	"timestamp"	TEXT,
	"event_code"	TEXT,
	"pii_hash"	TEXT,
	"confidence_score"	REAL,
	"integrity_hash"	TEXT,
	PRIMARY KEY("record_uuid"),
	FOREIGN KEY("event_code") REFERENCES "event_registry"("event_code")
);
CREATE TABLE IF NOT EXISTS "event_registry" (
	"event_code"	TEXT,
	"category"	TEXT,
	"source_tier"	TEXT,
	"methodology"	TEXT,
	"legal_basis"	TEXT,
	PRIMARY KEY("event_code")
);
CREATE TABLE IF NOT EXISTS "final_commit" (
	"filepath"	TEXT,
	"content_sanitized"	TEXT,
	"approval_timestamp"	TEXT,
	"recruiter_id"	TEXT,
	"certificate_hash"	TEXT,
	PRIMARY KEY("filepath")
);
CREATE TABLE IF NOT EXISTS "job_dict" (
	"original"	TEXT,
	"neutral"	TEXT,
	"category"	TEXT,
	PRIMARY KEY("original")
);
CREATE TABLE IF NOT EXISTS "pending_review" (
	"filepath"	TEXT,
	"original"	TEXT,
	"output"	TEXT,
	"status"	TEXT DEFAULT 'PENDING',
	"integrity_hash"	TEXT,
	PRIMARY KEY("filepath")
);
CREATE TABLE IF NOT EXISTS "session_summary" (
	"session_uuid"	TEXT,
	"file"	TEXT,
	"pii_redacted"	INTEGER,
	"gip"	INTEGER,
	"trust_score"	REAL,
	"compliance_grade"	TEXT,
	"processed_at"	TEXT
);
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('66734d5e-1ad2-4581-9f85-298bdc48a501','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:24:05','T0-ANL','<NA>',1.0,'c503dbdeb1914f8fb60c66c597a25567a4b9e1f921d44d9911540908e8cce430');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('71a8e1a2-026d-43c9-8679-4d7abe065fc3','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:24:05','T0-ANL','<NA>',1.0,'26ded4732d077bcc9dc12aecf8f17c7380ec973e06cd5a5186cd67e7dbb81268');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f0f64411-07d3-49b4-a773-afe8bdd5403f','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:24:05','T0-ANL','<NA>',1.0,'7052cad818c95fd6e0cea9574d46d5934334caadbfbb670b27ad1f18e8e4edc7');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3682ae11-60a5-447a-96d4-9d8b1a5b36f4','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:24:05','T0-ANL','<NA>',1.0,'cdc8c9d248588980ffe6c1957f8a278d9e40c5f92231693502611fe0de3cb0dd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('669dd0d5-25d0-42cd-bb95-37f146586e46','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:24:06','T0-ANL','<NA>',1.0,'df6b2d8a072d4cfeab0eb0f314ee682e5b22100ea705ff19fb9f03c7365e242e');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('ab319102-c9fe-42ff-bfbe-c9753f01983c','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:09','T1-RGX','79439e48a7ae261d384d7fa0d6c53eba7084bc7b0d6997927ab84c50d07019b3',1.0,'5d4097fb1c5537f9c2eecba71003331bd592f17ea0104e4ddbd70c3cbb6f7d68');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('248a96d0-24dc-4a5c-896c-d9a01d00dc08','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:09','T1-RGX','2ee8ae1971b72ce761c34be73a666f18b18204030db012b32b83ddd1e6c76919',1.0,'da087212cfe52e820a09637033cb2cccb54deafd663ac6b040d9b9f1db475125');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c85f9e3c-32a3-4bbe-b32e-e7143b4ef1c4','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:09','T1-RGX','1fbc486f56b702794fe709d21b621fcedfddec5c3b47fdaaad3a40fa4e830d1b',1.0,'4b85518790bc9dbd6d80bc4210cf5339c16d474c46f707f06eb4403e3e75a41b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3a1cea68-a107-4edf-b106-a218ce296330','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:09','T1-RGX','ac7bb74de6884ffce919c15fef4193749d4588026c643973946713ac46da540d',1.0,'b1ff65506d377e519dff3a7a5dd804a1d4e6430135c1ca3e6a3f8524fea178cc');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('74465e80-a6a9-4370-9d98-17723a4f8cf4','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:09','T1-RGX','197258ca7af8a0237e0142a6a134eebb3865f709ac600f174ccafd9b5732b11a',1.0,'f4cd17c538805288fceab6c83c2cde985a3d5b94b8bbb4b74fd6fe4a57ebd9f9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('61f89c03-7eab-411e-be4c-8aa1e924e65a','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:09','T1-RGX','af59d975cc129cfae20ed3dc13322b3da5c8d844157550ba79fd4aefc4c454d2',1.0,'0eb66052a94403b42ca6ff96dde967484dfdca582d0ba349ff386e20bd4b44c8');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f19b3f40-6f6a-45f7-957c-f0789e5b4690','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:09','T1-RGX','55eb98af205c9d17e3569de62916a94b7944672c772f526e6e4c957c0b8d5eeb',1.0,'93a249bf347ba03917684baf1d05e4c9932af7877e15ace4a1e07af7c3c98735');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('88af9e8c-82c9-4d09-8f77-9358d14cd980','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:09','T1-RGX','79439e48a7ae261d384d7fa0d6c53eba7084bc7b0d6997927ab84c50d07019b3',1.0,'fa297b126d4c0faf3733bf754cf63b85608f2b9b266401666ea19515ef9ccfa9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('68a9a21c-72a9-4fc8-927d-9eba7df1b7ca','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:09','T1-RGX','1814d559d903a355adc7a53dce316c9951ed3051a3dc835caed2a5e5b2642539',1.0,'54fedd581cc5224b9529ce512dca1a594a3bd515c624f380d0f603d31ee77d8a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fce5fcb5-011a-476a-ab38-16cd2c28bd60','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:09','T1-RGX','1fbc486f56b702794fe709d21b621fcedfddec5c3b47fdaaad3a40fa4e830d1b',1.0,'460e4ff86f445b569426233938342a6a0a968d098dced1805de06a22e5000da2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3e29ec93-284f-41a6-9eb3-d63e94cfa871','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:09','T1-RGX','0a5021255973689d14938f512754626b4cd797fada7a0b686ffe9515617d84e7',1.0,'ae99df5ac91acda332a4a8f2dcaa795ab9b1ab316aa70ef490ce54f5b7bfe4ae');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('bdd5265d-cbc9-40f0-bcb5-735f5b5e2aad','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','bc057bc1b6a03b41ccd61fe131197fb30e235dba0750bd25b5f1d7d6f0874220',1.0,'706c1ac02d10567d264d2df7a69f13cf70bf0ab42516d93bf90ca92962d9f6af');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fdff1806-17fe-47c5-90ab-425437f6552a','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','57a3283d833b65c8a6e8d1acb9c99b8a895296ecf28f4795d666b72cb7f0732f',1.0,'8f7603a5518bfeb4636484b70dda2753554eac1e4a225eb4c6a89dacbc62e91a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('4e4db5b8-ffe5-46be-9532-49a51de80b7c','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','8f914541867dd2e2f380f5fbaddb63ab71bc324db2aa93af410b91ef83df8918',1.0,'7c08d0d89dcf59d0eb650f6473f86b6a3d51370047dded151d8ad409949babf2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('62b1711b-efc5-4be2-9016-44dabc5b9bf2','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','11eb3890c7358e243299891c0debb1cece829ff97849e319022236e2ac844b83',1.0,'a43ab884bfd0a58e423414cdfc8e2ed9624932f80629853a39ca0daf4aa75efb');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('19d2a3bd-fda4-42b8-b66c-3723a6c7f89b','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','1667e6d0887ef07e608546609f0b3b5739ac440e126847c5e60181fa942145a3',1.0,'d6e919c25b4346dc8afeae8665de200cde75746dbbe59190f3b8e4e48ecced9c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('ee4709a4-3197-4a3d-84aa-431abefa4713','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:09','T1-RGX','cae88c87edf0b4dad1cbe69c2b50abb2c600827e55fe7affa1b33a12ee7ab725',1.0,'c60e58c5f6f85d4dd58e1405d6019eb77d77cac15318275f600199eb2f58430b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('5b079791-f2dc-405e-a169-5d5e5bbd0db2','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:09','T1-RGX','197258ca7af8a0237e0142a6a134eebb3865f709ac600f174ccafd9b5732b11a',1.0,'1c38fd9a6dd121f55913ca473a011a2d6c410288593abe0e953c26fccf6e2f6c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1f7a37fe-14a1-42a5-ba13-8e8be357cdb7','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:09','T1-RGX','af59d975cc129cfae20ed3dc13322b3da5c8d844157550ba79fd4aefc4c454d2',1.0,'560fe0a004bffe05f7a894fff817e499e9a2d71c13cb1b77094721fe846d231a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('2a22720e-6714-4e2c-b42a-ea13880d376b','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:09','T1-RGX','55eb98af205c9d17e3569de62916a94b7944672c772f526e6e4c957c0b8d5eeb',1.0,'9a5f0a2bed3b810240cab5096b05c41e279c518e20f4508074332d76c907ba95');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('cc24babf-223c-437f-aa75-303986325f14','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:09','T1-RGX','79439e48a7ae261d384d7fa0d6c53eba7084bc7b0d6997927ab84c50d07019b3',1.0,'26b4b7f3f5ea0826fb2f80f0037825cffa44fb4d74c4baa47dffcddbd417620c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('56534c01-7a6a-44a7-a347-590910d3d880','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:09','T1-RGX','1814d559d903a355adc7a53dce316c9951ed3051a3dc835caed2a5e5b2642539',1.0,'562b8c0fa2bbe863cb2fe19a65c33fd46f8e366574f10aebd6527b33d4bb3192');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('10e1f372-ee39-4d23-93ad-e75a8994c1ea','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:09','T1-RGX','1fbc486f56b702794fe709d21b621fcedfddec5c3b47fdaaad3a40fa4e830d1b',1.0,'df2946ea6ed9378fe6d8d437dbdf5848c70f7a78a661aaf1b75cab791120c4f4');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('476aa17c-d452-4ba7-8d62-41aa96fbb3ce','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:09','T1-RGX','64337060b501af87d29116d7a8c1dcb0185c4bea5f3e66421fd387a9d22b0975',1.0,'923b6521d25f2b7f4c06e4284085cd7c02acc9c2f47b52c668d6986f308e24a0');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7434f5df-8dc1-48e0-9d4a-5ba603ec2e85','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:09','T1-RGX','0a5021255973689d14938f512754626b4cd797fada7a0b686ffe9515617d84e7',1.0,'5c40e785fe2b36eb2c767b00d7c7fb22150224ceb703252a4d0254b67b8f101c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('a3689bc5-754c-4285-a448-34a012a4953a','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:09','T1-RGX','5055c9148e306a0a099a6a67c65662d4aefe982609b5778f4ce05c54e83a4ae5',1.0,'64aa464d5c4a9eeeecc4e8f502d8343e794a3884f3eb52eb9bb84708295d66dd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('cf75f7bf-1ffa-49c4-a5ac-0fc157ab0c66','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:09','T1-RGX','4f311213ea90a42299e61213d5adcc25c16f8e081565ca19f3c4940f78035c96',1.0,'f9f009aaeac2b77eef4b5afbdb67b106b3f2f53c9a69f945b504fa37e1ab9558');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('20a8acd9-084e-42b5-8463-8c40a6d5d202','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:09','T1-RGX','554cc477587db5c33dae7d9505a7fd1241ba22d450940cf2bae0eac549c6219e',1.0,'9d0847b33f2db4ce6497cb1838f86a18b6292aa145f84a0b52aa379adf7311b3');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7d237a97-e114-49e1-abb8-eda6b2386a6e','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:09','T1-RGX','fe033cfbdef717e43cca8dfb53c44434de58dea140bcb6391195387324402878',1.0,'791f9f9f33ede7fadb0691affe44975ddcd16254941c662e81fa1cd21ab49cfe');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('dfeee938-5fcc-4ebd-ae12-725fdba39e48','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:09','T1-RGX','11eb3890c7358e243299891c0debb1cece829ff97849e319022236e2ac844b83',1.0,'452f9db889fbc23e9cc6e961d27620175f0fd2a18e028cfa5dc118ce18b70303');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d61506fc-486b-47da-8990-ccf850f0a1e4','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','0ec17fc71c4d0d90312d5d7b5da085f4ba99c11fc0e50731055bdf6b397ff81e',1.0,'b7772f24dbcb76f50562342fbefe9c98a41c5ec7d60dd4b651d7b66f3bceec4c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('8ef6faea-6512-4fc0-ab29-27bc0823ca37','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','f91008207ef499cd19c3be622e3f4c8a62cbce0fe6bcdea34882dabe49a5d49c',1.0,'439348e3a8b51dbf8b5396ffc9525ab53a7577f8ec7e388225b589401f51f825');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('b9ec4d2b-a9e9-49fa-a325-ea7023885905','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'e840f6ed1440c197b529fa8b99bc2ae877d3c243cbeec72867b1606d94b7a0a9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('846673c6-9db9-498b-97dc-b0593d61fbac','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','e03bb8a19b6aa9c82cce531705a29664253574d81e2c04168870ae53d18be351',1.0,'26508644693cf912fee2256b61ddd9259bdc070c8b3faa3fc7f4f842eb169239');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1a97cfbf-3f05-4f18-a1ba-41184e3b4438','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'e840f6ed1440c197b529fa8b99bc2ae877d3c243cbeec72867b1606d94b7a0a9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7bb892a1-d6c4-4f75-86f8-72b539c4c7f0','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','47afcff3dcb9e9891e7b329e65a7ea4e9f42f7176299c068a3e8a95f6bd705cf',1.0,'fc764e50caa57e67d9ad7d9bd3b4544cbbae60631d861b67d0c535688965c05c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('5d870d12-053b-4224-a9d2-729071a336d3','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'e840f6ed1440c197b529fa8b99bc2ae877d3c243cbeec72867b1606d94b7a0a9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('8892c124-5882-455a-af7c-f12f8e9cb203','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:13','T2-NER','65119ff9eada47bcc2ddff6a0d59d909fe04367c3159b938d1620919ff18653c',1.0,'0eed2532f16b334d4d381dbf87b576fc93ef7979186ea7a7028076c63adfab16');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('a0da3e9b-1893-4eda-832c-5d83434f2be4','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','06b23a2c049e2d3fc306b15419b22b47272da9632b092f1e2a51f6c910b373d0',1.0,'749fd3d2bf6cdf6c1dfde2322eefd0cd15dbd8a93477c2db72b4fe6fa259741a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3df7d932-9b44-47fc-8d77-ebd483f2fdf8','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','c075b9c24a3d0f0cdad3e99683ed2514981e4ff40c6c0056de53e5e56e052227',1.0,'01231ab0390bca3ad8af7d859a97e55b8af9e00aa712f0ac9066262d40e50719');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7972ed06-b048-48c1-9bd8-74621ef8ddf8','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','71b4f3a3748cd6843c01e293e701fce769f52381821e21daf2ff4fe9ea57a6f3',1.0,'e0a1321ca66a995914c0ef5bd8662b9fce30bb1de4313ef44d97e99cd2e36467');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('0a9db330-7c99-439b-a95f-15a22cb8cabc','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','7580e51171e610a887b8548667cb82a07100fc8da33d18ed86f0314451b6ef0b',1.0,'4a00975bc02f7606ea171680cb7f3097ca6707176ecceca28162353915522df7');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('4ad2b85a-c772-4417-bb2e-f3ea1c5b7f0b','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','c075b9c24a3d0f0cdad3e99683ed2514981e4ff40c6c0056de53e5e56e052227',1.0,'01231ab0390bca3ad8af7d859a97e55b8af9e00aa712f0ac9066262d40e50719');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('5754dede-1b0d-48f7-86c2-6ee3b094fa6f','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:13','T2-NER','af6e56aacd8097c3fb7597b08ecb3d87a040f6ab58067a4b8ff9f5b747adb9be',1.0,'4de5c0dc981290151b1bf33b21cdeb08b12e2306d65cd51574f88bddc496f8d0');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('48272014-a32d-4cfe-897e-149f124f22bb','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','94666c8824a80401cc53f85069615b39616d05058ffb1e36beb7093e1bbaf409',1.0,'8695e14eaec2e29706150093c45439467face043f8ee59b3aabe3ec9561ee97c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('bc5d79af-5254-45c0-8f5f-4b3c542feaa3','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'3f292dcb8ff1ecef89e216057e84e247db8e4ea7f44467bd613702cfddc49074');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('dfb8b1fa-18f8-4ea4-bf0b-2cd3798c2d1d','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','af6e56aacd8097c3fb7597b08ecb3d87a040f6ab58067a4b8ff9f5b747adb9be',1.0,'37d1f59b0d3900067d8584f84a0a3d451f57fa0cf81b5f3cb68d4a4bd60bfa0e');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('a805832f-b7c3-4a98-92b4-05eb066a0e69','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','7f51ee44529574f764e001c66fe1d8fe682a4e4fdbb3cf4df616963fd947331b',1.0,'ccb35a170a502179ef4b33d8d5f1011b05ba5a4830e807d8ea25a352903e0212');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('49136df7-a324-4189-8407-a485cef80fa2','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'3f292dcb8ff1ecef89e216057e84e247db8e4ea7f44467bd613702cfddc49074');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fac0bd9a-014b-4b6c-80e6-2a586fd989d9','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','6814ef46f686990cf4e946f966167b0507e1d642c44e51f61bffb0bba2d4672b',1.0,'da6e3c2fe7796f5d781d122c1ee9a93a1297e18b6fc774f260b18975610fe550');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('50f17d84-444e-4c61-a378-47e9da9d1ddc','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:13','T2-NER','384283b118f398a667f3026592358cc3cefaa0cac8d5a86a8702f975ef4eb7ac',1.0,'1d43ae3ba8418e6737948066f19067ef1dd431b257442668d9de43ab0fe796d9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('916915d1-bb52-4b11-808f-4d0bf64d5d25','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:13','T2-NER','257d0c535f5c3186b05ec9e303a24b7f00e4ddeef056e511d5108190f2cb8e89',1.0,'8e376483885fc9f9a6ec5457f4224058516053a45a6ba73eb3fbdcb119d897ad');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('e85ee11b-bd9e-4f91-b7ab-de25f995f218','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:13','T2-NER','2318776eed9ae62ec1c5640ebc0c673cc72274c5af8f484ecbb416a198fcaaa9',1.0,'2ee0fe09d5c61d2626f03dad4075142f8be20670606e652906edd7b2ea93c583');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('af7ef877-d583-4830-9804-4a69ad3cb3f1','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:13','T2-NER','cba156a671524f06b9b6bf0c7cf4f80ea24a7e630d47391b9d575358289f5abc',1.0,'500a9e45098a540338b584acf91be46e2eb55e4e74a3168c32872936aa05ef7c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('6e537b60-bbbc-477b-a01f-0da4704f91d4','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:13','T2-NER','2318776eed9ae62ec1c5640ebc0c673cc72274c5af8f484ecbb416a198fcaaa9',1.0,'2ee0fe09d5c61d2626f03dad4075142f8be20670606e652906edd7b2ea93c583');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7441b2e4-17c6-4030-9693-8fd261b66f18','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:13','T2-NER','fc3872c12cb13dc05d5fd811d319324ccc1e1ef90c08476cbd64bf254a216372',1.0,'d20543275abdca3ab5fa90bf5376af77c7850acde7e8306385beab1fff7a6aa1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('0fad2e8d-b1c5-4d4a-b9cb-2d6ba9f87d73','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','9ce4e9689c826e407c8d4d00b757824fa6518e08b7b11f5fc908d38d44f3cd38',1.0,'f14c4b35aa40b309be6d3c9c53e3d71ac3349f1a54427c62c850107629ee918a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('6f26b810-e8e5-489d-bd22-4e83441baa99','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','bc278e4754bd4dec621c5f2844072837b71bfeb66480938a0bcad9a11ab563e0',1.0,'caf2c2485364fa67d9a7714a17cc76917fb92704da89a7dcf91f2793c3b04548');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('eb873b3f-daf7-4d5a-b9ff-9336f6f704bc','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','f7e898f114a558333016790c8b8ba3aa0118d7dc4fb8dd451a0fdca583f8a66d',1.0,'f7b19e081b8ca7e8c51a553d84956a0a15735cb8d75f59ac48dde2b5688f0402');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d89e25f9-e48f-4d7d-8fd1-061335f72c4a','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','dbe8ce381da4cba8821626b7d3f32a4ecc4045d5d585704e97b65300ca629a2a',1.0,'fcbbbe45e6cd1c68f2fc3a369b4dc1b32d081ba2867a1a624f477f80bd625fa9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('53f302cc-91d1-48fc-a549-fb94dcbe24f6','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','028ffac895cba8386cfe9060ba0818d4f1dabd95fd2c694593f225bcd3067ad4',1.0,'c137c133c3d60996b6e1b4cdcc615083d4b320681d1faa2686cb3d06b16fe6ae');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('cea3197c-1a51-40ec-a4d1-dfeb0bbcc25e','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','e03bb8a19b6aa9c82cce531705a29664253574d81e2c04168870ae53d18be351',1.0,'509358d4c524c5885cd5022896becf411b78d3eb7d247d0b11fb13180202a311');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3f3159da-363f-4d90-a836-fecf8a006732','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','af6e56aacd8097c3fb7597b08ecb3d87a040f6ab58067a4b8ff9f5b747adb9be',1.0,'b8be1eda108a99a6b80151b49398c2f4166f559e3ccd8edd3b72b7e4da8f4263');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('495440b4-3f37-406f-93f5-e26434f08203','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','98e84bcb60524e1b6d59b328fbf2eb9297187a31db64c0307c32266c213e5252',1.0,'44752d58de249853a12885cb0327ad825f3566202b1f2c664a960f2b5ab43ed4');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('44a9b304-3b5b-4cc7-8ef4-9d0b97627a62','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','384283b118f398a667f3026592358cc3cefaa0cac8d5a86a8702f975ef4eb7ac',1.0,'ee30dc4713adfb23efbb02df35d7124ef4456829d2189ce89b81ecc7fca96eb6');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('903b1e42-dfbf-4529-b669-1bf82bc4f692','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','a96f37052c23114b163ee513d7456b527421b6b30b6a5846bcd9c83faa595bb2',1.0,'fafe1ff3a00bafb54a194b9da3d05d3ab303459b8dac98fac80779beae54863f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('6d08c415-21bd-4da1-97cb-35e31d4fbf4e','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','c075b9c24a3d0f0cdad3e99683ed2514981e4ff40c6c0056de53e5e56e052227',1.0,'7348fad4daa4cabf1468369ea4618607f9ceed539f82489b2aca2eb4acf9babc');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('a45b0362-1554-4605-b179-61aede5ec9cc','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','076be49c6e5ea6922b83da2a20f8f86dcf6682d988f38320e8fe3603044f1aae',1.0,'ecda0216bfc9d29befc09fa80e73f33ca3bf76eab8f014c6846bca2df1776e5f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7575b7dc-81d2-4e48-be4a-e881937d8d26','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','7d8ba31ecd3cd673d67e93024612a0d699c1a929fd6f59e12733208f35919416',1.0,'c2c3c4bf558ef7da1d36a59bb7435823971b7e731683e13d1f0fde950569f0ce');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('b3d45b4d-1ea7-441d-80a3-a66e0842da58','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:13','T2-NER','028ffac895cba8386cfe9060ba0818d4f1dabd95fd2c694593f225bcd3067ad4',1.0,'c137c133c3d60996b6e1b4cdcc615083d4b320681d1faa2686cb3d06b16fe6ae');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('6f22e989-98d1-4686-9a6a-bfd784a03901','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','94666c8824a80401cc53f85069615b39616d05058ffb1e36beb7093e1bbaf409',1.0,'8e26fe3a221714ae783d1cd523f381d0a45ef4a23f4cb47205fa603700c1d342');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1198aec8-7edf-4038-92c4-21247f04d996','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'17146e8b1d975191fa298028588f1e376b3aa559ee64d5683bea01b6a787da74');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c1c555e0-7755-4515-863c-4716ab2947f1','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','af6e56aacd8097c3fb7597b08ecb3d87a040f6ab58067a4b8ff9f5b747adb9be',1.0,'0a4d6d8f8e06ee397dce1d8cbf0fa447f603238a3241146427959b15c6530460');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fe8e70a0-37ad-4011-b14f-9ac31cfe890a','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','7f51ee44529574f764e001c66fe1d8fe682a4e4fdbb3cf4df616963fd947331b',1.0,'2406378a8f5e65a3d00de35e71c8460f1f4bc720cf5feb3ae6fe1ad7c75019a5');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f8d2dc21-3f4b-4683-beac-f47c4c4db764','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','dad114b6ed7342bac65c79575f6c7ff761ec26b52c1f5f7a9110532973d05df2',1.0,'17146e8b1d975191fa298028588f1e376b3aa559ee64d5683bea01b6a787da74');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d337cad3-34be-421e-91e4-8ddde13b97a0','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:13','T2-NER','384283b118f398a667f3026592358cc3cefaa0cac8d5a86a8702f975ef4eb7ac',1.0,'62fa6633e1ae21d4ca2f20b5989269b96e0bfe15952ba10779baa12657303323');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('e5c3800d-3c36-4c7c-b456-5c5cba3be035','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','bf74e4a280affafbdf6692bc6a9f3d66b03094fbfb4a91589bc7fd6b32664fdb',1.0,'9605b0103f641306a90e9b3c309bbfb50379bbcabf635302930febd7d5d72dc3');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c97ab0d2-78f4-40e5-b1e6-1f3ac175b4cb','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','2568c214b558e6845023c8a8d775d61c48eac326e5a36f6a44d6e78b6cffcb2a',1.0,'f0163d7c1257516b6b587b93c2dc0b19687d34024825d7b7642a7a9882c52969');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('571afebe-708e-4072-a428-9a3cc51f306a','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','c075b9c24a3d0f0cdad3e99683ed2514981e4ff40c6c0056de53e5e56e052227',1.0,'37c7b71fc15e1397543d65b5ead6e49133d3f7720f1e6df1ceb63e3cf9cec346');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3f9e6fbd-00f3-4629-b099-4ca5cde64b85','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','93e16e6fc8351c593b06a36f63c255415caa5276504fa20af4f10f4c825d70b9',1.0,'90567cc03ab76ee96bb4cca9012cdc2c6b9bf1e7ff30d8fb7101aa18056e3404');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('2ac2b107-8927-49ea-af34-c789cdbf6dc2','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','85fadee31bd52f1165087953010c73ff35cde9c835e6d03beb35e398db8afc70',1.0,'bb82cc5ebb59409bf458d37290e985c9b7ed155171830dbbc51d19a3308aa67a');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3ef16aa1-dc79-481c-98b2-3887819df8f7','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','7d5af1837f8a559b14c3dea2fb9a4d5eab5580798c2fc21bffdee4c7e991edd8',1.0,'f08766db70935547bb7b96048db36c7ba5e06ac52b871741381add499f21813b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('4761ae3b-6962-4572-8893-f622f136c483','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','29cda29977a3ef8d4d9e546e03e630a9a97e4903dce13f3d2fca2db38b3a01f3',1.0,'5dc0794e63fd1ca7148bdb765914686d92da3a52a39fc4d4a42cbffc067a9a5b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d0c5c507-befd-4523-9e1c-600c0064a686','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','ddcdda5ac2be57d4e9c122e1cbc299856dfd6ccaaaf583a77645536d9636bbe9',1.0,'08d298290dac165eea3d4683f847ad063473ee5641a7bb670b9a8568fb3e44cf');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('84fc8207-9f0c-494c-937d-d5099714370b','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','7401ba2d22d623a10b9685d9efdb8fd539f204a9490ebdd3273297a7cbbd7743',1.0,'41a0ac6f140d40c2010ef8b95cb2d398a8bc7ea36a089c05bf344d1173ab5cc2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f3ad1c04-2f60-4bf3-bba2-f5366dfa2b7f','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','0fbdda687fcdbf66af48d7277dd3a1b6c8259c04164abbb86ed8cfb619c174b4',1.0,'9c39622a4f00e5d0f82ced41000431c168e681c887657b8a6cdcd8821c58beba');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('bd118a6a-dc33-4c2f-bb0e-65089c0d7049','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','0fbdda687fcdbf66af48d7277dd3a1b6c8259c04164abbb86ed8cfb619c174b4',1.0,'9c39622a4f00e5d0f82ced41000431c168e681c887657b8a6cdcd8821c58beba');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('b1342e8f-b9ec-4fc5-9a15-8cc24a1e6af9','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:13','T2-NER','384283b118f398a667f3026592358cc3cefaa0cac8d5a86a8702f975ef4eb7ac',1.0,'7df65a8e58c48ee1e68e3bcb494ab5b64a3abde81de4965094a154218716054b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('ada31783-af7c-4bdd-a620-67de97910ba7','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-GIP','a42276dc3bca61ca7db7eb36512513facbf1e1a412409c891c13cb216d9184ed',0.9,'eea5698b0bcece5c48f1103a5828329b77b624f03e03b16004321f1f9510ca8c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('450460d7-6734-4d10-9f7e-9cbc23f94caf','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c79f9caf-57c9-4bbf-b667-8b81949f1362','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('dc1a0f91-7c38-4c97-83f1-a513200c2b76','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','c0bc1e08f9743b2d50d5f1607503bf4e849af0e729fca896515bea955d70a33e',0.75,'c6c85b99d5b65bc21799b5451ee5327cf6431126e97c307ffff1eee4a7510233');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c3c952a4-4c23-42be-aed1-01ca59ae6e4b','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','eaa1aebfd86b461569632acaa47523a66d33a9f768c819802f1934cf07ed24aa',0.75,'91a440559a3718df590d887b6df3f39726a8d4511b0fd0f2455f9fb119a294dc');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('6822cf72-b4ee-43a8-b2bd-9883ad908e44','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','6bf004dcd179c1f207828dc31525bbc4a29925c52458ff12b789e36d3b0d1fd2',0.75,'cb4155a9424b2008299a1819723e6a691b529f9d482dfc7165601eb7053758c7');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f6647099-7c22-4ae9-9d17-43fbdb812ce7','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('33fc9168-6a2d-4b21-917d-482f62f6bc89','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fa642184-4d4a-4411-bc15-b8308ae38cab','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','482b98e1609bd828db30a1c85f78a5e6e6ee55dcfb01db094432c1db2c1ae168',0.75,'7a8a0a2666bb30c6c534b7faf11bb77b8fe4b42a0ff46d2d1fdf8ce1009f95d2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('056f38e4-ba83-4a63-8967-cb574c48badf','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1be5e88f-d035-47ef-9e72-00e1ba08e7fa','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('b36a3eb4-e51d-483b-a9c7-5c8e012cbc2a','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','eaa1aebfd86b461569632acaa47523a66d33a9f768c819802f1934cf07ed24aa',0.75,'91a440559a3718df590d887b6df3f39726a8d4511b0fd0f2455f9fb119a294dc');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fcb33614-ce56-4c60-840a-40b4ca983a24','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f45b912a-7e5b-482f-a542-30db76888bcf','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','a95cdd258f9bd357a6ea7efb973b6ab20450a6f68a7f654eb8a57964efd080f0',0.75,'18a3b64595f233ad7a1ff892a648e1017b161b342479e3627017388a8f46df5d');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('31375c81-6044-4bba-938e-a20252b7207a','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','ed6d1ff9927b323ba8ec93a8701da3b7840bdd36bb46fe8a9721a9200090780f',0.75,'b16cdefec213b15b35276e0fb0c54d4d3350012ef69ddfe667f1f1c98934caee');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('84a6135b-7f86-47b5-b5f6-a220538a376d','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','eaa1aebfd86b461569632acaa47523a66d33a9f768c819802f1934cf07ed24aa',0.75,'91a440559a3718df590d887b6df3f39726a8d4511b0fd0f2455f9fb119a294dc');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c5c8e248-92e2-418b-9f19-de78e64ff400','/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','20.02.2026 14:25:16','T3-FLG','3557b1c6fa8946cc8864f2410a2ea9b70c5b551ac96d772c52cd91721322e4df',0.75,'1b4a96d6edb5cc1e1232c8249c5bcd9ff59ebecf76bacaebfad313751783145c');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('008da465-785e-403d-ab24-843eda0239a5','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('dbc98a7b-3210-4f8f-a3ab-14813cd2290e','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('39a46e42-422a-4acf-ac92-7dc9d51d2000','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('dc1390d1-1d7e-4d37-94d1-467c10a82ff4','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','e3a1c7313e9a0779481a3d48b11f72f32f57d22eb1c298fd8292a60b50ce9e8c',0.75,'c1bd99cdfed1f7206697bbe9b594df824c00efc494c809b2373857d5398bfa4e');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d931fc3a-a7e7-4a75-a712-01202b1b9779','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('9366e456-488d-4186-bcb9-878c990b6625','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1f15a423-ced6-445b-b68a-b7ec459ea74b','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','a21daa1880017b9dc34bad45190017f5d2a8e5f73defa8311897821be522e55d',0.75,'514af7d9b5c6caf22ae68a5aa92372038a2ce3fd099874664a46b579cb91c5fd');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d13b3d50-2430-417e-872f-5af878c66f89','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','6bf004dcd179c1f207828dc31525bbc4a29925c52458ff12b789e36d3b0d1fd2',0.75,'6db4db161ea1c3c1cfed8d55765a32913683ca918212645898db4c59dad19b7f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('3342ac9d-55a2-4c92-b923-964de4439605','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','5f2b0cc78934385587c2d6f5cd003101e8dd096109adf6cb66b5559f804f017d',0.75,'d5341b83b97470c2ee7e74532efaba7aa10468aa7f07c15004c1c273d0d1dd5f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('46cfa9a2-971e-405b-bcfa-81de6a38be90','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','1e9720af1c3d46c8025d6b5a8204594bc353e8853a6d6b20547c32ad612534e8',0.75,'07693ebb25936fe484ae75dd607bd1bba7b4264d4f18033b17ed077abaa7b3f2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('518ff782-d9e4-4bee-9d72-f803dd1c2c01','/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'b224695d59cf336dc914d93a1d36754c91cb1649fe581fafc4db84ce1722f780');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('da3f2646-4c11-430b-af68-984a1dc96614','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:16','T3-FLG','5dabf059842755a55dbaac2b1fb2a6a5c0a8521ebe0af3da27860c6d96ac605d',0.75,'5476182f08aacce9c9aca4ed8266526d6914f44e7df9cce7006f2fb01ee9d1b1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('cb346497-e132-4f94-9793-f8914fd0884c','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:16','T3-FLG','ffbc32175897f96210dd5e385442344b7196870a505412e394e3edc26723286a',0.75,'d9029f48d34f5e699ec024cd4036e6c2cbe13525be36fd92f37b754e43223bce');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('939f831e-719f-4fab-b5ed-053241184129','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'7367c5f0794be2ef04e6b20c9b3fa96e55f0352a6a1840b9c22676f79cc3a39f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7f730d71-a700-4e0f-a376-24136feb5061','/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'7367c5f0794be2ef04e6b20c9b3fa96e55f0352a6a1840b9c22676f79cc3a39f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d4f7ec30-998b-4520-947e-ce47aa60b2d7','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'da81b9d489dd144b037ec09bd66086df4d05419d6b7790e1f6d1a8ded9e869d2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7836ae7a-aad9-441f-a888-ce02de511794','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'da81b9d489dd144b037ec09bd66086df4d05419d6b7790e1f6d1a8ded9e869d2');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d3242887-4298-48ac-ae79-f9e5331837eb','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','6b60c2ef62ccf55245de56480951c9fbabafab2ae57a2a6b4d61e4fd45f48119',0.75,'ea66e0ac226434b16a8cc1ab5cfe447d8a76544e7537fefa11360c778de14004');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('2e30d685-6b25-43ca-bf39-509e434b18e7','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','6b60c2ef62ccf55245de56480951c9fbabafab2ae57a2a6b4d61e4fd45f48119',0.75,'ea66e0ac226434b16a8cc1ab5cfe447d8a76544e7537fefa11360c778de14004');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('9b8385df-c489-4413-93cb-d034ba399204','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','fa23b3bc413a6b55e96e8d6e1db0888465b790e92d58c49354a61092f5e84f7b',0.75,'38979c85706ec42e0889c5dfc4e8a59890219ee8e11fbf9a5a650ac321659a0d');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('561fe72c-a34c-4293-99bf-9b0369355ba9','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'506fad77f6c8b667016bc3150df202dd354dad07ab5c27fb514bacd4dfa7fee7');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('a63c9ab9-f816-4c91-92f1-0e61aff94303','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','ccae499316d9373675a2374c1bc827264e5612561490aebd2c5db7e9fdcf498a',0.75,'8cae756c97b3e8d2dffec99b0348b63d20665d4784e2cdfe3fca307aba594115');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c879ed81-4679-4d29-8ce1-5b3a8300883d','/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','20.02.2026 14:25:16','T3-FLG','80652d939cb9fbf070bfd9ae25af62b77aa2c049ddd9ad6c4f2b00000256e73e',0.75,'30bb9b1c8795bd690e828faf5db50f82ed935a1acb6459e1c0c41940ad2f9722');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('fef7380a-c477-42b2-b49a-52ef6ba566f9','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-GIP','74b7eef93f131b1dc54803335895c71ac192167c21b2f26c7ddddcb91e27519d',1.0,'f1e85373f3aca44f7b3935dd5b418e3584f01c3bfb06734f70d1005660919de5');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('f67650f2-3c1d-4af6-9afd-e47bae0676c3','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','a73add1aecea03a894ca65d99bc5e91d21b58cdb728343bbcb6cf6cf38b809f5',0.75,'735f735b88ed2c994d7c5eec9e3c61791008875fcaa33a74419daaea5445d568');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('e6773006-a502-466e-b67c-7c4591a6bc36','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','d04fd59f3d9a1fd424c47874ae1dab0dde54fa73ba474245bfac79279afe6df7',0.75,'83ba88ec912e4e61059f5f2b694ac68032924bfc3bcbc3a54847bff6631ba53d');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('398178fb-87aa-462e-89fd-3c2d9c4e721f','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','78cd68013a72c7755b4a9b3941b8138d834140f017c14631d4f46a489823ae9e',0.75,'55d8741f0cea5bc7f7e086b91745f6a08c4ea6bd74f2ec95dab8a31dd7a08fbe');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('872920f0-fe9b-449d-bb71-af75af8817ea','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'74abc372ca589114a38c6f6f197e7f34e43b1db9b603a061d001b41e76450fc1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('898470fb-ca00-4001-b7c8-1661e46b544f','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'74abc372ca589114a38c6f6f197e7f34e43b1db9b603a061d001b41e76450fc1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d28d97cb-709b-482a-bc57-6e29847c948b','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'74abc372ca589114a38c6f6f197e7f34e43b1db9b603a061d001b41e76450fc1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('652f47d7-2f07-47a4-8120-2fc4a76d499d','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','4e425901c513bb380b43697595e3640c43794040acec56d2c3aa8f205062ea51',0.75,'74abc372ca589114a38c6f6f197e7f34e43b1db9b603a061d001b41e76450fc1');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('9c36e5f9-7b0f-459b-be45-2f7ba8286c67','/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','20.02.2026 14:25:16','T3-FLG','e72fa00cbe72a828389cb978b7f0209ad9207bead832e2b5fe3d7a5ec52c45f1',0.75,'497e34e924cc1992252db1a788ddde591fe3bf4abbf2eae280633c0a156ad521');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1d6abf4e-be71-4d89-8363-d1865e4fe4c9','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-GIP','0f153ef173cef2d7892b4173b7a58d2930e3d3d9bc37bc504dc50389c00f3360',0.9,'55f08a3afaac4afded9568c491dd166025a29a7bce3255b7a0a3bf0fc75fd73f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('c7a36506-5eb1-46ac-8912-333f0b026f31','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','5dabf059842755a55dbaac2b1fb2a6a5c0a8521ebe0af3da27860c6d96ac605d',0.75,'ee60dc36b6993281837719a49a0271724ad52e61ae05bcdcb43a053a8dc5bd1f');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d5a6750b-4cac-43be-834c-4853f2bc6bf7','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','64f6e01ef0e38fbec022b46e1949d7019a152f61b0f6c5b29b1fe8d50f3906dc',0.75,'8c50db46e7653b074dc2e0156207cfa4b502076ddaa13aa771d830117a329d9b');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('9c50bd83-ee7f-4d1b-8a05-174d06d75548','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','1a1b9ecbd7acbd2d9ecd014d759281413e2c9abd20e0c3f0d31a0fca282aab65',0.75,'da21bae739bfe922a45e240ec926273c29df84753bcb3be6fb590a8a97556d91');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('37b24bb9-1857-4704-b3bf-330467cf113f','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'76d401ddd2d70e835da5496b7930b2731b6bea8ed416113abccbced2215bffe6');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('cf5ca0e1-0cad-4963-937d-70eb7b151097','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','00f1b7d3b1b91eed63812885af220dc80c6834a5f448246c2a0309be5e9e94db',0.75,'daeec4b182585d852a0cbc79ddad9be6d2567c228a3ce1e577b6f9e2114cddf9');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('d69643bf-eb91-447e-9abe-7aea03e6619b','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'76d401ddd2d70e835da5496b7930b2731b6bea8ed416113abccbced2215bffe6');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('7e24e4ef-9be5-4c74-9062-3df5021556cc','/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','20.02.2026 14:25:16','T3-FLG','a484d08c63ac98a79b1f2dca8096d706fe15cf7d0c3d5e9afb304d14a41bf18d',0.75,'76d401ddd2d70e835da5496b7930b2731b6bea8ed416113abccbced2215bffe6');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('eb86676a-b509-4bb6-b465-a299be187028','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:16','T3-FLG','bf74e4a280affafbdf6692bc6a9f3d66b03094fbfb4a91589bc7fd6b32664fdb',0.75,'a5e36fe4599f6f5d33c8d1fd6984372747914ca6e9d3c5728ae30cd2676e9c92');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('0a749d98-59b5-44be-bd6a-7a69ecba82dc','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:16','T3-FLG','bf74e4a280affafbdf6692bc6a9f3d66b03094fbfb4a91589bc7fd6b32664fdb',0.75,'a5e36fe4599f6f5d33c8d1fd6984372747914ca6e9d3c5728ae30cd2676e9c92');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('1f6b5240-5079-4f6b-a441-aed9ce2b61fe','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:16','T3-FLG','71127078944ae1bcecee6773c46b0ef74008258b51cb3ea47adc04a7685e1aa7',0.75,'6eab5ce1db3542e5e0091938f47be77a628e49b8251a01ad3fe0606598e0d8ff');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('aa7f7036-44d1-4f41-af70-4a2e139782af','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:16','T3-FLG','71127078944ae1bcecee6773c46b0ef74008258b51cb3ea47adc04a7685e1aa7',0.75,'6eab5ce1db3542e5e0091938f47be77a628e49b8251a01ad3fe0606598e0d8ff');
INSERT INTO "audit_trail" ("record_uuid","filepath","timestamp","event_code","pii_hash","confidence_score","integrity_hash") VALUES ('2342ecaa-e8a9-4d3a-9cef-b5f0c4c84cdc','/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','20.02.2026 14:25:16','T3-FLG','fa23b3bc413a6b55e96e8d6e1db0888465b790e92d58c49354a61092f5e84f7b',0.75,'15f3cf773cd61f37f93078bde5469891664aaf86ec0e9b525a1f33bb94cf9212');
INSERT INTO "event_registry" ("event_code","category","source_tier","methodology","legal_basis") VALUES ('T0-ANL','System','Tier 0','Tika Parser Metadata Analysis','System Integrity');
INSERT INTO "event_registry" ("event_code","category","source_tier","methodology","legal_basis") VALUES ('T1-RGX','Privacy','Tier 1','Deterministic REGEX Matching','GDPR / DSGVO');
INSERT INTO "event_registry" ("event_code","category","source_tier","methodology","legal_basis") VALUES ('T2-NER','Privacy','Tier 2','Probabilistic Named Entitiy Recognition','GDPR / DSVGO');
INSERT INTO "event_registry" ("event_code","category","source_tier","methodology","legal_basis") VALUES ('T3-GIP','Inclusion','Tier 3','Linguistic Gender Neutralization','AGG / EU AI Act');
INSERT INTO "event_registry" ("event_code","category","source_tier","methodology","legal_basis") VALUES ('T3-FLG','Inclusion','Tier 3','Morphological Gender Flagging','EU AI Act / D&I');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Erzieher','Pädagogische Fachkraft','Sozialpädagogik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Erzieherin','Pädagogische Fachkraft','Sozialpädagogik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Erzieher*in','Pädagogische Fachkraft','Sozialpädagogik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lehrer','Lehrkraft','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lehrerin','Lehrkraft','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lehrer*in','Lehrkraft','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Dozent','Lehrende','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Dozentin','Lehrende','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Dozent*in','Lehrende','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Professor','Hochschullehrende','Hochschule');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Professorin','Hochschullehrende','Hochschule');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Professor*in','Hochschullehrende','Hochschule');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Arzt','Medizinische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ärztin','Medizinische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Arzt*Ärztin','Medizinische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Arzt*in','Medizinische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Krankenpfleger','Pflegefachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Krankenschwester','Pflegefachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Pflegekraft*','Pflegefachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Physiotherapeut','Therapeutische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Physiotherapeutin','Therapeutische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Physiotherapeut*in','Therapeutische Fachkraft','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Psychologe','Psychologische Fachkraft','Psychologie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Psychologin','Psychologische Fachkraft','Psychologie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Psycholog*in','Psychologische Fachkraft','Psychologie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ingenieur','Technische Fachkraft','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ingenieurin','Technische Fachkraft','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ingenieur*in','Technische Fachkraft','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Informatiker','IT‑Fachkraft','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Informatikerin','IT‑Fachkraft','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Informatiker*in','IT‑Fachkraft','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Entwickler','Softwareentwicklung','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Entwicklerin','Softwareentwicklung','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Entwickler*in','Softwareentwicklung','IT');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Projektleiter','Projektleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Projektleiterin','Projektleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Projektleiter*in','Projektleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Teamleiter','Teamleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Teamleiterin','Teamleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Teamleiter*in','Teamleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Abteilungsleiter','Abteilungsleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Abteilungsleiterin','Abteilungsleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Abteilungsleiter*in','Abteilungsleitung','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Manager','Management','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Managerin','Management','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Manager*in','Management','Management');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sachbearbeiter','Sachbearbeitung','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sachbearbeiterin','Sachbearbeitung','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sachbearbeiter*in','Sachbearbeitung','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mitarbeiter','Mitarbeitende / Beschäftigte','Allgemein');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mitarbeiterin','Mitarbeitende / Beschäftigte','Allgemein');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mitarbeiter*in','Mitarbeitende / Beschäftigte','Allgemein');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäufer','Verkaufskraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäuferin','Verkaufskraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäufer*in','Verkaufskraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kassierer','Kassenkraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kassiererin','Kassenkraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kassierer*in','Kassenkraft','Handel');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Handwerker','Fachkraft im Handwerk','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Handwerkerin','Fachkraft im Handwerk','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Handwerker*in','Fachkraft im Handwerk','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Elektriker','Elektrofachkraft','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Elektrikerin','Elektrofachkraft','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Elektriker*in','Elektrofachkraft','Handwerk');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mechaniker','Kfz‑Fachkraft / Technik','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mechanikerin','Kfz‑Fachkraft / Technik','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Mechaniker*in','Kfz‑Fachkraft / Technik','Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Bauarbeiter','Bau‑Fachkraft','Bau');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Bauarbeiterin','Bau‑Fachkraft','Bau');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Bauarbeiter*in','Bau‑Fachkraft','Bau');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Architekt','Architekturfachkraft','Architektur');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Architektin','Architekturfachkraft','Architektur');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Architekt*in','Architekturfachkraft','Architektur');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Designer','Designfachkraft','Kreativ');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Designerin','Designfachkraft','Kreativ');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Designer*in','Designfachkraft','Kreativ');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Künstler','Kunstschaffende','Kunst');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Künstlerin','Kunstschaffende','Kunst');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Künstler*in','Kunstschaffende','Kunst');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Journalist','Redaktionsmitarbeit','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Journalistin','Redaktionsmitarbeit','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Journalist*in','Redaktionsmitarbeit','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fotograf','Fotografie','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fotografin','Fotografie','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fotograf*in','Fotografie','Medien');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Berater','Beratung','Consulting');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Beraterin','Beratung','Consulting');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Berater*in','Beratung','Consulting');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Trainer','Trainingsleitung / Coaching','Training');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Trainerin','Trainingsleitung / Coaching','Training');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Trainer*in','Trainingsleitung / Coaching','Training');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Coach','Coaching','Beratung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Coach (w)','Coaching','Beratung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Coach*in','Coaching','Beratung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Referent','Fachreferat','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Referentin','Fachreferat','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Referent*in','Fachreferat','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sekretär','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sekretärin','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sekretär*in','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Assistent','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Assistentin','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Assistent*in','Assistenz','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Personalreferent','Personalwesen','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Personalreferentin','Personalwesen','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Personalreferent*in','Personalwesen','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Recruiter','Recruiting','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Recruiterin','Recruiting','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Recruiter*in','Recruiting','HR');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Buchhalter','Finanzbuchhaltung','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Buchhalterin','Finanzbuchhaltung','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Buchhalter*in','Finanzbuchhaltung','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Controller','Controlling','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Controllerin','Controlling','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Controller*in','Controlling','Finanzen');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäufer im Außendienst','Außendienst','Vertrieb');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäuferin im Außendienst','Außendienst','Vertrieb');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verkäufer*in im Außendienst','Außendienst','Vertrieb');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Serviceberater','Kundenservice','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Serviceberaterin','Kundenservice','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Serviceberater*in','Kundenservice','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kundenbetreuer','Kundenbetreuung','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kundenbetreuerin','Kundenbetreuung','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Kundenbetreuer*in','Kundenbetreuung','Service');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Pflegehelfer','Pflegeassistenz','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Pflegehelferin','Pflegeassistenz','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Pflegehelfer*in','Pflegeassistenz','Gesundheit');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Logopäde','Logopädische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Logopädin','Logopädische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Logopäd*in','Logopädische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ergotherapeut','Ergotherapeutische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ergotherapeutin','Ergotherapeutische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Ergotherapeut*in','Ergotherapeutische Fachkraft','Therapie');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sozialarbeiter','Soziale Fachkraft','Soziales');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sozialarbeiterin','Soziale Fachkraft','Soziales');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Sozialarbeiter*in','Soziale Fachkraft','Soziales');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verwaltungsangestellter','Verwaltungstätigkeit','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verwaltungsangestellte','Verwaltungstätigkeit','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Verwaltungsangestellte*','Verwaltungstätigkeit','Verwaltung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Hausmeister','Haustechnik','Gebäude / Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Hausmeisterin','Haustechnik','Gebäude / Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Hausmeister*in','Haustechnik','Gebäude / Technik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fahrer','Fahrdienst','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fahrerin','Fahrdienst','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Fahrer*in','Fahrdienst','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lagerarbeiter','Lagerlogistik','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lagerarbeiterin','Lagerlogistik','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Lagerarbeiter*in','Lagerlogistik','Logistik');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Wissenschaftler','Forschende','Wissenschaft');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Wissenschaftlerin','Forschende','Wissenschaft');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Wissenschaftler*in','Forschende','Wissenschaft');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Student','Studierende','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Studentin','Studierende','Bildung');
INSERT INTO "job_dict" ("original","neutral","category") VALUES ('Student*in','Studierende','Bildung');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/313-lebenslauf-einer-erzieherin.pdf','E R Z I E H E R I N

## LENA SCHMIDT

## K O N T A K T

+49 176 234 5678 Blumenstraße 12, 10115 Berlin anna.mueller@email.de

## B E R U F S Z I E L

Engagierte und empathische Erzieherin mit über fünf Jahren Erfahrung in der frühkindlichen Bildung. Mein Ziel ist es, Kinder individuell zu fördern, ihre sozialen Fähigkeiten zu stärken und eine liebevolle Lernumgebung zu schaffen.

## F Ä H I G K E I T E N

-  Einfühlungsvermögen
-  Geduld im Umgang mit Kindern Empathie
-  Teamfähigkeit
-  Organisationstalent
-  Grundkenntnisse
-  Gute EDV-Kenntnisse

## S P R A C H E N

-  Deutsch: Muttersprache.

-  Englisch: Gut

- 

- Spanisch: Grundkenntnisse

<!-- image -->

<!-- image -->

## B E R U F S E R F A H R U N G

## ERZIEHERIN

Kita Sonnenschein

August 20XX – heute| Berlin

Betreuung und Förderung von 20 Kindern im Alter von 3 bis 6 Jahren. Planung und Durchführung pädagogischer Aktivitäten und Projekte. Dokumentation der Entwicklung jedes Kindes.

## ERZIEHERIN IM ANERKENNUNGSJAHR

Kita Regenbogen

September 20XX – Juli 20XX| Berlin

Unterstützung bei der Organisation des täglichen Gruppenalltags. Durchführung kreativer Bastel- und Musikangebote. Dokumentation der Entwicklungsfortschritte der Kinder.

## ERZIEHERIN

Kita Kleine Entdecker

Januar 20XX – Juli 20XX | Hamburg

Durchführung von Projekten zu Themen wie Natur, Jahreszeiten und soziales Miteinander.

Organisation von Elternabenden und regelmäßiger Austausch über den Entwicklungsstand der Kinder.

## A U S B I L D U N G

20XX – 20XX

## STAATLICH ANERKANNTE ERZIEHERIN

Fachschule für Sozialpädagogik, Berlin Schwerpunkt auf frühkindlicher Bildung

20XX – 20XX

## ALLGEMEINE HOCHSCHULREIFE

Gymnasium am See, Potsdam

©AZURIUS – Modeles-de-cv.com','Pädagogische Fachkraft

## [PER]

## Kontakt

[PHONE_DE] [LOC_STR2], [LOC] [LOC] [EMAIL]

## Berufsziel

Engagierte und empathische Pädagogische Fachkraft mit über fünf Jahren Erfahrung in der frühkindlichen Bildung. Mein Ziel ist es, Kinder individuell zu fördern, ihre sozialen Fähigkeiten zu stärken und eine liebevolle Lernumgebung zu schaffen.

## Fähigkeiten

-  Einfühlungsvermögen
-  Geduld im Umgang mit Kindern Empathie
-  Teamfähigkeit
-  Organisationstalent
-  Grundkenntnisse
-  Gute Edv-Kenntnisse

## Sprachen

-  Deutsch: Muttersprache.

-  Englisch: Gut

- 

- Spanisch: Grundkenntnisse

<!-- image -->

<!-- image -->

## Berufserfahrung

## Pädagogische Fachkraft

Kita Sonnenschein

August 20XX – heute| [LOC]

Betreuung und Förderung von 20 Kindern im Alter von 3 bis 6 Jahren. Planung und Durchführung pädagogischer Aktivitäten und Projekte. Dokumentation der Entwicklung jedes Kindes.

## Pädagogische Fachkraft [PER] Anerkennungsjahr

Kita Regenbogen

September 20XX – Juli 20XX| [LOC]

Unterstützung bei der Organisation des täglichen Gruppenalltags. Durchführung kreativer Bastel- und Musikangebote. Dokumentation der Entwicklungsfortschritte der Kinder.

## Pädagogische Fachkraft

Kita Kleine Entdecker

Januar 20XX – Juli 20XX | [LOC]

Durchführung von Projekten zu Themen wie Natur, Jahreszeiten und soziales Miteinander.

Organisation von Elternabenden und regelmäßiger Austausch über den Entwicklungsstand der Kinder.

## Ausbildung

20XX – 20XX

## Staatlich Anerkannte Pädagogische Fachkraft

Fachschule für Sozialpädagogik, [LOC] Schwerpunkt auf frühkindlicher Bildung

20XX – 20XX

## Allgemeine Hochschulreife

Gymnasium am See, [LOC] – [WEB]com','PENDING','1b518a4530c920baae5f0bd7654a00d54c71598a0bd0e6c2cc851eafce5ecae1');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/283-lebenslauf-abitur.docx','**Abiturient**

**NAME UND NACHNAME**

<!-- image -->

Ludwig-Gymnasium München – 20XX – 20XX

lukas.schneider@email.de

Sonnenstraße 18, 80331 München

©AZURIUS – Modeles-de-cv,com

Motivierter und engagierter Abiturient mit großem Interesse an Wirtschaft und internationalen Beziehungen. Ich zeichne mich durch Teamfähigkeit, Organisationstalent und Verantwortungsbewusstsein aus und suche nach einer Möglichkeit.

Social Media Tools

Photoshop

MS Office

**Allgemeine Hochschulreife (Abitur)**

**Fremdsprachenzertifikat Englisch**

**FÄHIGKEITEN**

Teamfähigkeit

Organisation

Kommunikationsstärke

**INTERESSEN**

Internationale Wirtschaft

Reisen und Sprachen

Sport (Fußball, Laufen)

Französisch

Englisch

Deutsch

**SPRACHEN**

Canva

**KENNTNISSE**

München, Deutschland

Cambridge B2 First – 20XX – 20XX

**AUSBILDUNG**

- Organisation von Freizeitaktivitäten für Jugendliche.
- Unterstützung bei Veranstaltungen und Workshops.
- Mitarbeit bei der Vorbereitung von Informationsveranstaltungen.

**Freiwilliger**

Jugendzentrum München – 20XX - 20XX

- Unterstützung im Kundenservice und bei administrativen Aufgaben.
- Mitarbeit bei der Vorbereitung von Informationsveranstaltungen.

**Schülerpraktikum**

Sparkasse München – 20XX - 20XX

- Unterstützung des Marketing-Teams bei der Planung von Werbekampagnen.
- Erstellung von Präsentationen und Pflege der Social-Media-Kanäle.

**BERUFSERFAHRUNG**

BMW AG – 20XX - 20XX

**Praktikant im Marketing**

+49 176 12345678

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->','**Abiturient**

**Name Und Nachname**

<!-- image -->

Ludwig-Gymnasium [LOC] – 20XX – 20XX

[EMAIL]

[LOC_STR2], [LOC] [LOC]

©Azurius – Modeles-de-cv,[PER]Motivierter und engagierter Abiturient mit großem Interesse an Wirtschaft und internationalen Beziehungen. Ich zeichne mich durch Teamfähigkeit, Organisationstalent und Verantwortungsbewusstsein aus und suche nach einer Möglichkeit.

Social Media Tools

Photoshop

MS Office

**Allgemeine Hochschulreife (Abitur)**

**[PER] Englisch**

**Fähigkeiten**

Teamfähigkeit

Organisation

Kommunikationsstärke

**Interessen**

Internationale Wirtschaft

Reisen und Sprachen

Sport (Fußball, Laufen)

Französisch

Englisch

Deutsch

**Sprachen**

Canva

**Kenntnisse**

[LOC], [LOC]

Cambridge B2 First – 20XX – 20XX

**Ausbildung**

- Organisation von Freizeitaktivitäten für Jugendliche.
- Unterstützung bei Veranstaltungen und Workshops.
- Mitarbeit bei der Vorbereitung von Informationsveranstaltungen.

**Freiwilliger**

Jugendzentrum [LOC] – 20XX - 20XX

- Unterstützung im Kundenservice und bei administrativen Aufgaben.
- Mitarbeit bei der Vorbereitung von Informationsveranstaltungen.

**Schülerpraktikum**

Sparkasse [LOC] – 20XX - 20XX

- Unterstützung des Marketing-Teams bei der Planung von Werbekampagnen.
- Erstellung von Präsentationen und Pflege der Social-Media-Kanäle.

**Berufserfahrung**

Bmw AG – 20XX - 20XX

**Praktikant im Marketing**

[PHONE_DE]

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->','PENDING','833f9825299ee7aaf0d6d919721e9e6bb2ce1b332383e6085d282d1515416b94');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/275-lebenslauf-vorlage-schüler.pdf','## ANNA MÜLLER

SCHÜLER

## PERSÖNLICHE DATEN

Geburtsdatum: 12. Mai 2007

Geburtsort: Berlin, Deutschland

Adresse: Sonnenstraße 45, Berlin

Nationalität: Deutsch

## SPRACHEN

Deutsch: Muttersprache

Englisch: Gut (Schulnote 2)

Spanisch: Grundkenntnisse

## IT-KENNTNISSE

MS Word – Sehr gut (Schularbeiten und Projekte)

MS PowerPoint – Gut (Präsentationen und Schulprojekte)

## HOBBYS

Lesen

Programmieren (Python)

Freiwilligenarbeit

Schreiben

Reisen

<!-- image -->

## SCHULBILDUNG

Gymnasium Altona

## Berlin

- Schwerpunktfächer: Wirtschaft, Mathematik und Englisch.
- Aktuell: 11. Klasse
- Teilnahme an Schülerprojekten im Bereich Unternehmensgründung.

## Stadtteilschule Nord Berlin

- Mittlere Reife.
- Abschlussnote: 1,9.
- Teilnahme an Schülerzeitung und Schulprojekt Nachhaltige Stadt.

## FORMATION

## Praktikantin – CreativeAds GmbH Berlin, DE

- Unterstützung bei Social-Media-Kampagnen.

·

- Mithilfe bei der Erstellung von Präsentationen.

## Praktikantin – Sparkasse Hamburg

Hamburg, DE

- Einblicke in die Kundenberatung und Kontoführung.
- Unterstützung im Kundenservice und bei der Organisation von Terminen.
- Mitarbeit bei einem Schulprojekt zur Finanzbildung.

## REFERENZEN

Referenzen sind auf Anfrage verfügbar.

Berlin, den 13. Oktober 20XX

09/20XX – 07/20XX

anna.mueller@email.de +49 176 1234567

Seit 09/20XX

<!-- image -->

©AZURIUS – Modeles-de-cv.com

06/20XX

07/20XX','## [PER]

Schüler

## Persönliche Daten

Geburtsdatum: [DATE]

Geburtsort: [LOC], [LOC]

Adresse: [LOC_STR2], [LOC]

Nationalität: Deutsch

## Sprachen

Deutsch: Muttersprache

Englisch: Gut (Schulnote 2)

Spanisch: Grundkenntnisse

## IT-Kenntnisse

MS Word – Sehr gut (Schularbeiten und Projekte)

MS PowerPoint – Gut (Präsentationen und Schulprojekte)

## Hobbys

Lesen

Programmieren (Python)

Freiwilligenarbeit

Schreiben

Reisen

<!-- image -->

## Schulbildung

Gymnasium Altona

## [LOC]

- Schwerpunktfächer: Wirtschaft, Mathematik und Englisch.
- Aktuell: 11. Klasse
- Teilnahme an Schülerprojekten im Bereich Unternehmensgründung.

## Stadtteilschule Nord [LOC]

- Mittlere Reife.
- Abschlussnote: 1,9.
- Teilnahme an Schülerzeitung und Schulprojekt Nachhaltige Stadt.

## Formation

## Praktikantin – CreativeAds GmbH [LOC], [LOC]

- Unterstützung bei Social-Media-Kampagnen.

·

- Mithilfe bei der Erstellung von Präsentationen.

## Praktikantin – Sparkasse Hamburg

Hamburg, [LOC]

- Einblicke in die Kundenberatung und Kontoführung.
- Unterstützung im Kundenservice und bei der Organisation von Terminen.
- Mitarbeit bei einem Schulprojekt zur Finanzbildung.

## Referenzen

Referenzen sind auf Anfrage verfügbar.

[LOC], den 13. Oktober 20XX

09/20XX – 07/20XX

[EMAIL] [PHONE_DE]

Seit 09/20XX

<!-- image -->

©[PER] – [WEB]com

06/20XX

07/20XX','PENDING','52c38c2c626baee619e8c532bded8a5e708ea423b25e28af90fe23f58bd68f68');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/Lebenslauf_persoenlich_junior copy.pdf','## Tim Feldmann

## Junior Data Analyst · Leipzig

Adresse: Karl-Liebknecht-Str. 21, 04275 Leipzig Telefon: +49 176 1112223 E-Mail: tim.feldmann@gmail.com LinkedIn: linkedin.com/in/timfeldmann Instagram: @tim.codes Geboren: 19.02.1998 · Familienstand: ledig

## Über mich

Neugieriger Berufseinsteiger mit starkem Interesse an Daten, Visualisierung und gesellschaftlichen Fragestellungen. Nebenbei betreibe ich einen Statistik-Blog und spiele Bass in einer Indie-Band.

## Berufserfahrung

Junior Data Analyst – Research Lab GmbH (2023–heute) Werkstudent Data Analytics – Mobility Start-up (2021–2023) Praktikant Business Intelligence – Stadtwerke Leipzig (2020)

## Bildung

M.Sc. Statistik – Universität Leipzig (2021–2023) B.Sc. Wirtschaftsmathematik – Universität Jena (2017–2021)

## Fähigkeiten &amp; Tools

Python · R · PowerBI · Excel · Git · LaTeX

## Hobbys &amp; Sonstiges

Musik (Bass, Synthesizer) · Urban Gardening · Ehrenamtliche Nachhilfe · Vegetarier · Lieblingsbuch: ‚Thinking, Fast and Slow''','## [PER]

## Junior Data Analyst · [LOC]

Adresse: [LOC]. 21, [LOC] [LOC] Telefon: [PHONE_DE] E-Mail: [EMAIL] LinkedIn: [WEB]com/in/timfeldmann Instagram: [SOCI] Geboren: [PHONE_DE] · Familienstand: ledig

## Über mich

Neugieriger Berufseinsteiger mit starkem Interesse an Daten, Visualisierung und gesellschaftlichen Fragestellungen. Nebenbei betreibe ich einen Statistik-Blog und spiele Bass in einer Indie-Band.

## Berufserfahrung

Junior Data Analyst – Research Lab GmbH (2023–heute) Werkstudent Data Analytics – Mobility Start-up (2021–2023) Praktikant Business Intelligence – Stadtwerke [LOC] (2020)

## Bildung

M.Sc. Statistik – Universität [LOC] (2021–2023) B.Sc. Wirtschaftsmathematik – [LOC] (2017–2021)

## Fähigkeiten &amp; Tools

Python · R · PowerBI · Excel · Git · LaTeX

## Hobbys &amp; Sonstiges

Musik (Bass, Synthesizer) · Urban Gardening · Ehrenamtliche Nachhilfe · Vegetarier · Lieblingsbuch: ‚Thinking, Fast and Slow''','PENDING','749ce1bb33e091b4174e3681b522bd064db63736181e7ee1b97b5f6b85d730d9');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/243-lebenslauf-ausbildung.docx','**DIPLOMAS Y HOBBIES**

**Formaciones :** Diplomados, Congresos, xxxxxxxxxx xxxxxx xxxxxxxxx xxxxxxxxxxxxxxxxx

**Hobbies:** xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

**LUKAS SCHNEIDER**

Ausbildungsbewerbung: Industriekaufmann

<!-- image -->

ñ

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

**KONTAKTDATEN**

<!-- image -->

<!-- image -->

<!-- image -->

**PRAKTISCHE ERFAHRUNG**

<!-- image -->

**PRAKTIKANT IM VERTRIEBSBEREICH**

lukas.schneider@email.de+49 176 12345678

München, Deutschland

Sonnenstraße 14, 80331

<!-- image -->

SIEMENS AG | München

<!-- image -->

<!-- image -->

- Unterstützung bei der Erstellung von Angeboten und Kundenkommunikation.
- Mitarbeit bei der Organisation von Kundenterminen.
- Einblick in verschiedene kaufmännische Prozesse.

<!-- image -->

**IT-KENNTNISSE**

<!-- image -->

**PRAKTIKANT IM BEREICH MARKETING**

MS Office (Word, Excel)

<!-- image -->

BMW AG | München

SAP

<!-- image -->

**SCHULBILDUNG**

©AZURIUS – Modeles-de-cv,com

09 / 20XX – 06 / 20XX

**Allgemeine Hochschulreife (Abitur)**

*Maximilian-Gymnasium, München*

**Grundkurs Büroorganisation**

*IHK München*

- Unterstützung bei der Erstellung von Präsentationen und Marketingmaterialien.
- Mitarbeit bei der Pflege der Kundendatenbank und Durchführung von Marktanalysen.
- Teilnahme an Teammeetings und Präsentation eigener kleiner Projekte.
- Kommunikation mit Kunden per E-Mail und Telefon.

**Europäischer Computerführerschein**

ECDL

**SPRACHEN**

Juli 20XX – August 20XX

Mai 20XX

CRM-Systeme

Deutsch: Muttersprache

Englisch: Gute Kenntnisse

Französisch: Grundkenntnisse

**ZERTIFIKATE &amp; BESCHEINIGUNGEN**

**Projektmanagement-Grundlagen**

Online-Kurs IHK Akademie

Juli 20XX

München, den 14. Oktober 20XX

*Lukas Schneider*

<!-- image -->','**[PER] Y Hobbies**

**[PER] :** Diplomados, [PER], xxxxxxxxxx xxxxxx xxxxxxxxx xxxxxxxxxxxxxxxxx

**Hobbies:** xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

**[PER]**

Ausbildungsbewerbung: Industriefachkraft

<!-- image -->

ñ

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

**Kontaktdaten**

<!-- image -->

<!-- image -->

<!-- image -->

**Praktische Erfahrung**

<!-- image -->

**Praktikant [PER] Vertriebsbereich**

[EMAIL][PHONE_DE]

[LOC], [LOC]

[LOC_STR2], [LOC]

<!-- image -->

Siemens AG | [LOC]

<!-- image -->

<!-- image -->

- Unterstützung bei der Erstellung von Angeboten und Kundenkommunikation.
- Mitarbeit bei der Organisation von Kundenterminen.
- Einblick in verschiedene kaufmännische Prozesse.

<!-- image -->

**IT-Kenntnisse**

<!-- image -->

**Praktikant [PER] Bereich Marketing**

MS Office (Word, Excel)

<!-- image -->

Bmw AG | [LOC]

Sap

<!-- image -->

**Schulbildung**

©[PER] – Modeles-de-cv,com

09 / 20XX – 06 / 20XX

**Allgemeine Hochschulreife (Abitur)**

*[PER], [LOC]*

**Grundkurs Büroorganisation**

*Ihk [LOC]*

- Unterstützung bei der Erstellung von Präsentationen und Marketingmaterialien.
- Mitarbeit bei der Pflege der Kundendatenbank und Durchführung von Marktanalysen.
- Teilnahme an Teammeetings und Präsentation eigener kleiner Projekte.
- Kommunikation mit Kunden per E-Mail und Telefon.

**Europäischer Computerführerschein**

Ecdl

**Sprachen**

Juli 20XX – August 20XX

Mai 20XX

Crm-Systeme

Deutsch: Muttersprache

Englisch: Gute Kenntnisse

Französisch: Grundkenntnisse

**Zertifikate &amp; Bescheinigungen**

**[PER]**

Online-Kurs Ihk Akademie

Juli 20XX

[LOC], den 14. Oktober 20XX

*[PER]*

<!-- image -->','PENDING','4b83ac183f3cfdab8a7516a0be7f00f6f87e86f73d5c33d3f4745547b41eaf8e');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/lebenslauf_anna_mueller.pdf','## ANNA MÜLLER

SCHÜLER

## PERSÖNLICHE DATEN

Geburtsdatum: 12. Mai 2007

Geburtsort: Berlin, Deutschland

Adresse: Sonnenstraße 45, Berlin

Nationalität: Deutsch

## SPRACHEN

Deutsch: Muttersprache

Englisch: Gut (Schulnote 2)

Spanisch: Grundkenntnisse

## IT-KENNTNISSE

MS Word – Sehr gut (Schularbeiten und Projekte)

MS PowerPoint – Gut (Präsentationen und Schulprojekte)

## HOBBYS

Lesen

Programmieren (Python)

Freiwilligenarbeit

Schreiben

Reisen

<!-- image -->

## SCHULBILDUNG

Gymnasium Altona

## Berlin

- Engagierte Klassensprecherin
- leistungsorientierte Schülerin
- Teilnahme an Schülerprojekten im Bereich Unternehmensgründung.

## Stadtteilschule Nord Berlin

- Mittlere Reife.
- Abschlussnote: 1,9.
- Teilnahme an Schülerzeitung und Schulprojekt Nachhaltige Stadt.

## BERUFLICHE ERFAHRUNG

## Praktikantin – CreativeAds GmbH Berlin, DE

- Unterstützung bei Social-Media-Kampagnen.

·

Kreative Schreiberin

## Praktikantin – Sparkasse Hamburg

Hamburg, DE

- Serviceorientierte Praktikantin als engagierte Assistentin im Service Team.
- Unterstützung im Kundenservice und bei der Organisation von Terminen.
- Mitarbeit bei einem Schulprojekt zur Finanzbildung.

## REFERENZEN

Referenzen sind auf Anfrage verfügbar.

Berlin, den 13. Oktober 2025

09/20XX – 07/20XX

anna.mueller@email.de +49 176 1234567

Seit 09/20XX

<!-- image -->

©AZURIUS – Modeles-de-cv.com

06/20XX

07/20XX','## [PER]

Schüler

## Persönliche Daten

Geburtsdatum: [DATE]

Geburtsort: [LOC], [LOC]

Adresse: [LOC_STR2], [LOC]

Nationalität: Deutsch

## Sprachen

Deutsch: Muttersprache

Englisch: Gut (Schulnote 2)

Spanisch: Grundkenntnisse

## IT-Kenntnisse

MS Word – Sehr gut (Schularbeiten und Projekte)

MS PowerPoint – Gut (Präsentationen und Schulprojekte)

## Hobbys

Lesen

Programmieren (Python)

Freiwilligenarbeit

Schreiben

Reisen

<!-- image -->

## Schulbildung

Gymnasium Altona

## [LOC]

- Engagierte Klassensprecherin
- leistungsorientierte Schülerin
- Teilnahme an Schülerprojekten im Bereich Unternehmensgründung.

## Stadtteilschule Nord [LOC]

- Mittlere Reife.
- Abschlussnote: 1,9.
- Teilnahme an Schülerzeitung und Schulprojekt Nachhaltige Stadt.

## Berufliche Erfahrung

## Praktikantin – CreativeAds GmbH [LOC], DE

- Unterstützung bei Social-Media-Kampagnen.

·

Kreative Schreiberin

## Praktikantin – Sparkasse Hamburg

Hamburg, DE

- Serviceorientierte Praktikantin als engagierte Assistenz im Service Team.
- Unterstützung im Kundenservice und bei der Organisation von Terminen.
- Mitarbeit bei einem Schulprojekt zur Finanzbildung.

## Referenzen

Referenzen sind auf Anfrage verfügbar.

[LOC], den [DATE]

09/20XX – 07/20XX

[EMAIL] [PHONE_DE]

Seit 09/20XX

<!-- image -->

©[PER] – [WEB]com

06/20XX

07/20XX','PENDING','f88de707f71eb86242c68863ef92e79c9244df46797307b3ed05b1b321076aa0');
INSERT INTO "pending_review" ("filepath","original","output","status","integrity_hash") VALUES ('/Users/webdev/Documents/Complyable/small_batch/234-vertriebsingenieur-lebenslauf.pdf','), 2017

<!-- image -->

## KONTAKT

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

+49 151 23456789

jonas.schmidt@email.de

München, Deutschland

linkedin.com/jonas

## SPRACHEN

Deutsch: Muttersprache

Englisch: C1

Spanisch: B1

## KERNKOMPETENZ

EN

-  Proaktives Vorgehen
-  Analytische Fähigkeiten
-  Sorgfältige
-  Teamfähigkeit
-  Logisches Denken

## SOFTWARE

Forecast

CRM

PoC, Pilot

Excel

<!-- image -->

## INTERESSEN

-  Klettern
-  Radsport

München, den 07.11.2025

## Jonas SCHMIDT

## VERTRIEBS ENGINEER

## BERUFSPROFIL

Ergebnisorientierter Vertriebsingenieur (6+ Jahre) mit Schwerpunkt B2B-Lösungen im Maschinen- und Anlagenbau. Verbindet technische Expertise (Automatisierung, Sensorik, IIoT).

## BERUFSERFAHRUNG

## Senior Vertriebsingenieur

ABC Automation GmbH, München | 20XX – 20XX

-  Verantwortung für Enterprise-Kunden in Automotive &amp; Food.
-  Umsatzverantwortung: €6,2 Mio./Jahr, Wachstum +28% YoY.
-  Gewinn von 14 Neukunden über Value-Based Selling und PoCs.
-  Leitung technischer Angebote (SPS/SCADA/IIoT); Abschluss von 3 Rahmenverträgen (3-Jahreslaufzeit).
-  Einführung von MEDDIC → Verkürzung des Sales-Cycles um 23%.

## Vertriebsingenieur

Mechatronik Systems AG, Nürnberg | 20XX-20XX

-  Gebiet DACH, Fokus OEM-Kunden (Sondermaschinenbau).
-  Ausbau von 40→65 aktiven Accounts; Churn &lt;3%.
-  Technische Beratungen, Lastenhefte, TCO-Analysen, FAT/SATBegleitung.

## Werkstudent Vertrieb/Applikation

RoboTech GmbH, Augsburg | 20XX – 20XX

-  Unterstützung Pre-Sales, Demos mit Kollaborationsrobotern.
-  Unterstützung Pre-Sales, Demos mit Kollaborationsrobotern.
-  Einführung von CPQ; Angebotsdurchlaufzeit um -35% reduziert. Einführung von CPQ; Angebotsdurchlaufzeit um -35% reduziert.
-  Erstellung technischer Präsentationen und Benchmarks.

## AUSBILDUNG

## M.Sc. Mechatronik &amp; Automation

Technische Universität München (TUM), 2017

©AZURIUS – Modelos-de-curriculum.com

<!-- image -->','), 2017

<!-- image -->

## Kontakt

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

[PHONE_DE]

[EMAIL]

[LOC], Deutschland

[WEB]com/jonas

## Sprachen

Deutsch: Muttersprache

Englisch: C1

Spanisch: B1

## Kernkompetenz

EN

-  Proaktives Vorgehen
-  Analytische Fähigkeiten
-  Sorgfältige
-  Teamfähigkeit
-  Logisches Denken

## Software

Forecast

Crm

PoC, Pilot

Excel

<!-- image -->

## Interessen

-  Klettern
-  Radsport

[LOC], den [PHONE_DE]

## [PER]

## Vertriebs Engineer

## Berufsprofil

Ergebnisorientierter Vertriebsingenieur (6+ Jahre) mit Schwerpunkt B2B-Lösungen im Maschinen- und Anlagenbau. Verbindet technische Expertise (Automatisierung, Sensorik, IIoT).

## Berufserfahrung

## Senior Vertriebsingenieur

Abc Automation GmbH, [LOC] | 20XX – 20XX

-  Verantwortung für Enterprise-Kunden in Automotive &amp; Food.
-  Umsatzverantwortung: €6,2 Mio./Jahr, Wachstum +28% YoY.
-  Gewinn von 14 Neukunden über Value-Based Selling und PoCs.
-  Leitung technischer Angebote (Sps/[LOC]/IIoT); Abschluss von 3 Rahmenverträgen (3-Jahreslaufzeit).
-  Einführung von Meddic → Verkürzung des [LOC] um 23%.

## Vertriebsingenieur

Mechatronik Systems AG, Nürnberg | 20XX-20XX

-  Gebiet Dach, Fokus Oem-Kunden (Sondermaschinenbau).
-  Ausbau von 40→65 aktiven Accounts; Churn &lt;3%.
-  Technische Beratungen, Lastenhefte, [LOC], [LOC]/SATBegleitung.

## Werkstudent Vertrieb/Applikation

RoboTech GmbH, [LOC] | 20XX – 20XX

-  Unterstützung Pre-Sales, Demos mit Kollaborationsrobotern.
-  Unterstützung Pre-Sales, Demos mit Kollaborationsrobotern.
-  Einführung von [PER]; Angebotsdurchlaufzeit um -35% reduziert. Einführung von [PER]; Angebotsdurchlaufzeit um -35% reduziert.
-  Erstellung technischer Präsentationen und Benchmarks.

## Ausbildung

## M.Sc. Mechatronik &amp; Automation

Technische Universität [LOC] (Tum), 2017

©[PER] – [WEB]com

<!-- image -->','PENDING','ccc1693f8e4e99f4a7979477de3b1a74ef5ec50029f9139b02b5fb20db07e5c1');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','313-lebenslauf-einer-erzieherin.pdf',12,17,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','275-lebenslauf-vorlage-schüler.pdf',11,4,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','Lebenslauf_persoenlich_junior copy.pdf',11,8,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','lebenslauf_anna_mueller.pdf',11,8,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','234-vertriebsingenieur-lebenslauf.pdf',17,5,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','283-lebenslauf-abitur.docx',9,11,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
INSERT INTO "session_summary" ("session_uuid","file","pii_redacted","gip","trust_score","compliance_grade","processed_at") VALUES ('597e7f3e-4d92-403c-a751-7ebeb8c3cef0','243-lebenslauf-ausbildung.docx',17,9,0.8,'REVIEW_REQUIRED','20-02-2026 14:25:17');
CREATE VIEW ui_highlight AS 
                SELECT
                a.filepath,
                a.pii_hash,
                r.category,
                r.event_code,
                r.methodology,
                a.confidence_score
            FROM audit_trail a
            JOIN event_registry r ON a.event_code = r.event_code;
COMMIT;
