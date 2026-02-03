/**
 * Shared data for module dashboards
 * Auto-generated from tracking_dashboard.html
 *
 * Usage in HTML:
 *   <script src="modules_data.js"></script>
 *   <script>
 *     // Data available: progressData, suggestionsData, appliedData, improvementHistory, MODULE_FOLDER_MAP, binaryMetrics
 *     console.log(progressData.filter(d => d.module.startsWith('m01')));
 *   </script>
 */

const progressData = [
  {
    "data_source": "M01_ExtractOwnBrandEntities_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 10.0,
    "model": "gpt-4o-mini",
    "module": "m01_v1",
    "pass_rate": 30.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m01_v1_judge_20260120_003146",
    "summary": {
      "error": 0,
      "fail": 35,
      "pass": 15
    },
    "timestamp": "2026-01-20T00:31:46.961853",
    "total_evaluations": 50,
    "braintrust_id": "e6720eee-6f86-4b87-966b-0591de5ce8a5",
    "braintrust_name": "M01_ExtractOwnBrandEntities_V1",
    "dataset_id": "e2d331a7-e757-4b66-b87d-97151470a11e",
    "dataset_name": "M01_ExtractOwnBrandEntities_V1.1",
    "prompt_id": "df8c6f85-a4d3-4d14-b1a0-7e5bb656a31e",
    "prompt_version_id": "1000196492750038047",
    "temperature": 0,
    "created": "2026-01-15 18:24:47.415000+00:00"
  },
  {
    "run_id": "m01_v2_judge_20260120_014252",
    "module": "m01_v2",
    "prompt_version": "v2",
    "dataset_version": null,
    "model": "gpt-4o",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T01:42:52.118402",
    "data_source": "M01_ExtractOwnBrandEntities_v2_190126_1.csv",
    "summary": {
      "pass": 45,
      "fail": 55,
      "error": 0
    },
    "pass_rate": 45.0,
    "match_rate": 30.0,
    "total_evaluations": 100,
    "braintrust_id": "055d0fdd-56a6-414b-9c05-a4a7ae514dc9",
    "braintrust_name": "M01_V2_ExtractOwnBrandEntities_v3_190126_1",
    "dataset_id": "ecb73ce1-0090-40ef-bceb-0d71105aeca6",
    "dataset_name": "M01_ExtractOwnBrandEntities_V3",
    "prompt_id": "421c42b9-6270-48c3-bb8e-2f66c7d13817",
    "prompt_version_id": "1000196514722422966",
    "temperature": 0,
    "created": "2026-01-19 15:29:41.876000+00:00"
  },
  {
    "data_source": "M01_V3_ExtractOwnBrandEntities_v3_190126_gpt5.csv",
    "dataset_version": "v3",
    "match_rate": 40.0,
    "model": "gpt-5",
    "module": "m01_v3",
    "pass_rate": 60.0,
    "prompt_version": "v3",
    "rubrics_version": "v5",
    "run_id": "m01_judge_20260120_003124",
    "summary": {
      "error": 0,
      "fail": 20,
      "pass": 30
    },
    "timestamp": "2026-01-20T00:31:24.366747",
    "total_evaluations": 50,
    "braintrust_id": "34958fa0-920a-4e5c-92d1-aca1e8928381",
    "braintrust_name": "M01_V3_ExtractOwnBrandEntities_v3_190126_gpt5",
    "dataset_id": "ecb73ce1-0090-40ef-bceb-0d71105aeca6",
    "dataset_name": "M01_ExtractOwnBrandEntities_V3",
    "prompt_id": "c5acb5f9-c12f-4c07-a6bf-9ab852c34b6b",
    "prompt_version_id": "1000196515183306932",
    "temperature": 0,
    "created": "2026-01-19 17:40:09.715000+00:00"
  },
  {
    "run_id": "m01_v3_judge_20260120_165053",
    "module": "m01_v3",
    "prompt_version": "v3",
    "dataset_version": "v2",
    "model": "gpt-4o-mini",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T16:50:53.018799",
    "data_source": "M01_V2_ExtractOwnBrandEntities_v3_190126_1.csv",
    "summary": {
      "pass": 43,
      "fail": 32,
      "error": 0
    },
    "pass_rate": 57.3,
    "match_rate": 60.0,
    "total_evaluations": 75,
    "braintrust_id": "2d13701c-caa4-47dc-9e79-3536dff50b9e",
    "braintrust_name": "M01_V3_ExtractOwnBrandEntities_v3_190126_1",
    "dataset_id": "ecb73ce1-0090-40ef-bceb-0d71105aeca6",
    "dataset_name": "M01_ExtractOwnBrandEntities_V3",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-19 16:32:09.726000+00:00"
  },
  {
    "run_id": "m01_v3_gemini_judge_20260120_175907",
    "module": "m01_v3_gemini",
    "prompt_version": "v3",
    "dataset_version": "v3",
    "model": "gemini-2.0-flash",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T17:59:07.703280",
    "data_source": "M01_V3_ExtractOwnBrandEntities_v3_200126_gemini20flash.csv",
    "summary": {
      "pass": 26,
      "fail": 24,
      "error": 0
    },
    "pass_rate": 52.0,
    "match_rate": 50.0,
    "total_evaluations": 50,
    "braintrust_id": "76ce49e2-169a-4fd6-b665-c80cd4dd8102",
    "braintrust_name": "M01_V3_ExtractOwnBrandEntities_v3_201026",
    "dataset_id": "ecb73ce1-0090-40ef-bceb-0d71105aeca6",
    "dataset_name": "M01_ExtractOwnBrandEntities_V3",
    "prompt_id": "3cab2c30-7d68-4bd0-b5f9-576f762aba9e",
    "prompt_version_id": "1000196520076712727",
    "temperature": 0,
    "created": "2026-01-20T17:38:06.456955"
  },
  {
    "run_id": "m01_v4_gpt4omini_judge_20260121_105445",
    "module": "m01",
    "prompt_version": "v4",
    "model": "gpt-4o-mini",
    "pass_rate": 40.2,
    "match_rate": 64.6,
    "summary": {
      "pass": 199,
      "fail": 296,
      "error": 0
    },
    "timestamp": "2026-01-21T10:54:45.252884",
    "data_source": "M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4omini.csv",
    "source_type": "judge",
    "rubrics_version": "v5"
  },
  {
    "run_id": "m01_v4_gpt4o_judge_20260121_105501",
    "module": "m01",
    "prompt_version": "v4",
    "model": "gpt-4o",
    "pass_rate": 53.7,
    "match_rate": 77.8,
    "summary": {
      "pass": 266,
      "fail": 229,
      "error": 0
    },
    "timestamp": "2026-01-21T10:55:01.118871",
    "data_source": "M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4o.csv",
    "source_type": "judge",
    "rubrics_version": "v5"
  },
  {
    "run_id": "m01_v5_gpt5_judge_20260121_105113",
    "module": "m01",
    "prompt_version": "v5",
    "model": "gpt-5",
    "pass_rate": 48.9,
    "match_rate": 45.5,
    "summary": {
      "pass": 242,
      "fail": 253,
      "error": 0
    },
    "timestamp": "2026-01-21T10:51:13.234838",
    "data_source": "M01_V5_ExtractOwnBrandEntities_v5_210126_gpt5.csv",
    "source_type": "judge",
    "rubrics_version": "v5"
  },
  {
    "run_id": "m01_v5_gpt4omini_judge_20260121_111131",
    "module": "m01",
    "prompt_version": "v5",
    "model": "gpt-4o-mini",
    "pass_rate": 58.4,
    "match_rate": 73.7,
    "summary": {
      "pass": 289,
      "fail": 206,
      "error": 0
    },
    "timestamp": "2026-01-21T11:11:31.613499",
    "data_source": "M01_V5_ExtractOwnBrandEntities_v5_210126_gpt4omini.csv",
    "source_type": "judge",
    "rubrics_version": "v5"
  },
  {
    "run_id": "m01a_judge_20260120_164146",
    "module": "m01a",
    "prompt_version": "v1",
    "dataset_version": null,
    "model": "gpt-4o-mini",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T16:41:46.043155",
    "data_source": "M01A_ExtractOwnBrandVariations_v1_150126_1.csv",
    "summary": {
      "pass": 47,
      "fail": 33,
      "error": 0
    },
    "pass_rate": 58.8,
    "match_rate": 0,
    "total_evaluations": 80,
    "braintrust_id": "d6efa0aa-dcfa-436f-b9ea-1286b132cce7",
    "braintrust_name": "M01A_ExtractOwnBrandVariations_v1",
    "dataset_id": "77aa12e9-c829-4dd4-834e-658b08016a56",
    "dataset_name": "M01A_ExtractOwnBrandVariations_V1.1",
    "prompt_id": "416420ef-b087-4f2b-9ef5-d82edf7cdfbf",
    "prompt_version_id": "1000196492768459099",
    "temperature": 0,
    "created": "2026-01-15 18:33:24.651000+00:00"
  },
  {
    "data_source": "M01A_V2_ExtractOwnBrandVariations_v2_190126_gpt5.csv",
    "dataset_version": "v2",
    "match_rate": 0,
    "model": "gpt-5",
    "module": "m01a_v2",
    "pass_rate": 85.0,
    "prompt_version": "v2",
    "rubrics_version": "v5",
    "run_id": "m01a_v2_judge_20260120_004925",
    "summary": {
      "error": 0,
      "fail": 6,
      "pass": 34
    },
    "timestamp": "2026-01-20T00:49:25.922974",
    "total_evaluations": 40,
    "braintrust_id": "93256f77-c7f1-454d-aaca-9e783c0e94e6",
    "braintrust_name": "M01A_V2_ExtractOwnBrandVariations_v2_190126_gpt5",
    "dataset_id": "f651668c-997f-43fc-81ac-5bc00626c497",
    "dataset_name": "M01A_V2_ExtractOwnBrandVariations",
    "prompt_id": "7d24e0f6-30f0-4c3c-972e-568e12006701",
    "prompt_version_id": "1000196515592466206",
    "temperature": 0.3,
    "created": "2026-01-19 19:36:19.492000+00:00"
  },
  {
    "run_id": "m01a_v2_gemini_judge_20260120_180023",
    "module": "m01a_v2_gemini",
    "prompt_version": "v2",
    "dataset_version": "v2",
    "model": "gemini-2.0-flash",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T18:00:23.549595",
    "data_source": "M01A_V2_ExtractOwnBrandVariations_v2_200126_gemini20flash.csv",
    "summary": {
      "pass": 16,
      "fail": 24,
      "error": 0
    },
    "pass_rate": 40.0,
    "match_rate": 0,
    "total_evaluations": 40,
    "braintrust_id": "247f3bfa-0aa0-4eaa-9736-37fffd5f2b7b",
    "braintrust_name": "M01A_V2_ExtractOwnBrandVariations__v3_200126",
    "dataset_id": "f651668c-997f-43fc-81ac-5bc00626c497",
    "dataset_name": "M01A_V2_ExtractOwnBrandVariations",
    "prompt_id": "109010c1-ac17-41c1-b8c0-5fb9bc72be69",
    "prompt_version_id": "1000196520085091707",
    "temperature": 0,
    "created": "2026-01-20T17:39:24.571304"
  },
  {
    "run_id": "m01b_judge_20260120_164412",
    "module": "m01b",
    "prompt_version": "v1",
    "dataset_version": null,
    "model": "gpt-4o-mini",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T16:44:12.456362",
    "data_source": "M01B_ExtractBrandRelatedTerms_v1_150126_1.csv",
    "summary": {
      "pass": 60,
      "fail": 20,
      "error": 0
    },
    "pass_rate": 75.0,
    "match_rate": 0,
    "total_evaluations": 80,
    "braintrust_id": "001ee360-9389-4b79-aa7a-f0112b3b5d60",
    "braintrust_name": "M01B_ExtractBrandRelatedTerms_v1",
    "dataset_id": "4136035d-c741-459b-a107-6b185a92aa7b",
    "dataset_name": "M01B_ExtractBrandRelatedTerms_V1.1",
    "prompt_id": "8b4a666e-b140-4ba7-ba67-6be650f3a8b0",
    "prompt_version_id": "1000196492804019857",
    "temperature": 0,
    "created": "2026-01-15 18:36:40.366000+00:00"
  },
  {
    "run_id": "m01b_v1_gemini_judge_20260120_180149",
    "module": "m01b_v1_gemini",
    "prompt_version": "v1",
    "dataset_version": "v1",
    "model": "gemini-2.0-flash",
    "rubrics_version": "v5",
    "timestamp": "2026-01-20T18:01:49.553753",
    "data_source": "M01B_V1_ExtractBrandRelatedTerms_v1_200126_gemini20flash.csv",
    "summary": {
      "pass": 32,
      "fail": 8,
      "error": 0
    },
    "pass_rate": 80.0,
    "match_rate": 0,
    "total_evaluations": 40,
    "braintrust_id": "c282a922-d2cc-43df-9c0b-d0efede06049",
    "braintrust_name": "M01B_ExtractBrandRelatedTerms_v1_200126",
    "dataset_id": "4136035d-c741-459b-a107-6b185a92aa7b",
    "dataset_name": "M01B_ExtractBrandRelatedTerms_V1.1",
    "prompt_id": "0418bc9b-dfdc-4646-9bd7-e29e4f5e5cba",
    "prompt_version_id": "1000196520100979777",
    "temperature": 0,
    "created": "2026-01-20T17:41:36.314293"
  },
  {
    "data_source": "M02_ClassifyOwnBrandKeywords_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m02",
    "pass_rate": 100.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m02_judge_20260119_152217",
    "summary": {
      "error": 0,
      "fail": 0,
      "pass": 105
    },
    "timestamp": "2026-01-19T15:22:17.082655",
    "total_evaluations": 105,
    "braintrust_id": "6bf7505b-f415-4402-8cda-2900dcda62c3",
    "braintrust_name": "M02_ClassifyOwnBrandKeywords-cb97caef",
    "dataset_id": "53159951-ee6a-48b4-aad4-ae602e0b0c99",
    "dataset_name": "M02_ClassifyOwnBrandKeywords_V1.1",
    "prompt_id": "52bb2595-e579-44ca-ab2d-30e567049246",
    "prompt_version_id": "1000196491395355933",
    "temperature": 0,
    "created": "2026-01-15 13:02:23.977000+00:00"
  },
  {
    "data_source": "M02B_ClassifyOwnBrandKeywords_PathB_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m02b",
    "pass_rate": 100.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m02b_judge_20260120_005124",
    "summary": {
      "error": 0,
      "fail": 0,
      "pass": 70
    },
    "timestamp": "2026-01-20T00:51:24.520681",
    "total_evaluations": 70,
    "braintrust_id": "b45f1d36-8d7a-4ceb-8525-38a27b38cac5",
    "braintrust_name": "M02B_ClassifyOwnBrandKeywords_PathB_v1",
    "dataset_id": "7810034c-ef1c-4b0b-b78e-56c3f09754a7",
    "dataset_name": "M02B_ClassifyOwnBrandKeywords_PathB_V1.1",
    "prompt_id": "59b529ec-84e4-4678-93b0-a0781cd80234",
    "prompt_version_id": "1000196493217005689",
    "temperature": 0,
    "created": "2026-01-15 20:23:56.978000+00:00"
  },
  {
    "data_source": "M04_ClassifyCompetitorBrandKeywords_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m04",
    "pass_rate": 60.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m04_judge_20260119_204721",
    "summary": {
      "error": 0,
      "fail": 24,
      "pass": 36
    },
    "timestamp": "2026-01-19T20:47:21.027981",
    "total_evaluations": 60,
    "braintrust_id": "97867488-a3d2-4048-a251-a440c9275e49",
    "braintrust_name": "M04_ClassifyCompetitorBrandKeywords-bfc88c43",
    "dataset_id": "4f84a83f-088b-423a-9e87-3c90822c056f",
    "dataset_name": "M04_ClassifyCompetitorBrandKeywords_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 12:13:54.707000+00:00"
  },
  {
    "data_source": "M04B_ClassifyCompetitorBrandKeywords_PathB_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m04b",
    "pass_rate": 80.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m04b_judge_20260120_005238",
    "summary": {
      "error": 0,
      "fail": 8,
      "pass": 32
    },
    "timestamp": "2026-01-20T00:52:38.747693",
    "total_evaluations": 40,
    "braintrust_id": "93833f92-2aae-4d11-91fc-5a596d6eabf1",
    "braintrust_name": "M04B_ClassifyCompetitorBrandKeywords_PathB_v1",
    "dataset_id": "6173da1f-a3e4-4b1b-adb2-fabb2651b84f",
    "dataset_name": "M04B_ClassifyCompetitorBrandKeywords_PathB",
    "prompt_id": "2e81badf-ce5f-46da-9eec-d7b6f91584d7",
    "prompt_version_id": "1000196493004416041",
    "temperature": 0,
    "created": "2026-01-15 21:08:57.044000+00:00"
  },
  {
    "data_source": "M05_ClassifyNonBrandedKeywords_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m05",
    "pass_rate": 100.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m05_judge_20260120_002750",
    "summary": {
      "error": 0,
      "fail": 0,
      "pass": 4
    },
    "timestamp": "2026-01-20T00:27:50.770592",
    "total_evaluations": 4,
    "braintrust_id": "ae3bdb06-9db8-46b7-897c-6e14e8d34c70",
    "braintrust_name": "M05_ClassifyNonBrandedKeywords_v1",
    "dataset_id": "2b96246a-a4ec-4a26-a2b7-fc0371381f81",
    "dataset_name": "M05_ClassifyNonbrandedKeywords_V1.1",
    "prompt_id": "b591351d-6a14-42e2-8783-357c8b1556ab",
    "prompt_version_id": "1000196493232508940",
    "temperature": 0,
    "created": "2026-01-15 20:32:44.127000+00:00"
  },
  {
    "data_source": "M05B_ClassifyNonBrandedKeywords_PathB_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m05b",
    "pass_rate": 90.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m05b_judge_20260120_005310",
    "summary": {
      "error": 0,
      "fail": 2,
      "pass": 18
    },
    "timestamp": "2026-01-20T00:53:10.880745",
    "total_evaluations": 20,
    "braintrust_id": "546e570b-9b65-4eed-b08b-549b1bf408cd",
    "braintrust_name": "M05B_ClassifyNonBrandedKeywords_PathB_v1",
    "dataset_id": "a6e9b14a-702e-4ab8-bc82-1d30583a2d19",
    "dataset_name": "M05B_ClassifyNonBrandedKeywords_PathB_V1.1",
    "prompt_id": "793a831d-202f-496b-8629-2cadaf8d49d5",
    "prompt_version_id": "1000196492864935133",
    "temperature": 0,
    "created": "2026-01-15 19:56:51.514000+00:00"
  },
  {
    "data_source": "M06_GenerateProductTypeTaxonomy_gd1_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m06_gd",
    "pass_rate": 65.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m06_gd_judge_20260120_005445",
    "summary": {
      "error": 0,
      "fail": 21,
      "pass": 39
    },
    "timestamp": "2026-01-20T00:54:45.854644",
    "total_evaluations": 60,
    "braintrust_id": "72ed5c87-3d3a-4853-ace0-baba0bbbf81e",
    "braintrust_name": "M06_GenerateProductTypeTaxonomy_GD_v1",
    "dataset_id": "cce4a191-6a25-4185-8675-4bda102226da",
    "dataset_name": "M06_GenerateProductTypeTaxonomy_V1.1",
    "prompt_id": "ee5bb5ac-b613-4579-b462-a9b61455d34b",
    "prompt_version_id": "1000196486895942787",
    "temperature": 0,
    "created": "2026-01-15 21:29:31.014000+00:00"
  },
  {
    "data_source": "M06_GenerateProductTypeTaxonomy_sd1_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m06_sd",
    "pass_rate": 65.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m06_sd_judge_20260120_005620",
    "summary": {
      "error": 0,
      "fail": 21,
      "pass": 39
    },
    "timestamp": "2026-01-20T00:56:20.386036",
    "total_evaluations": 60,
    "braintrust_id": "7158973d-d40a-4d32-ad37-81805bb5831d",
    "braintrust_name": "M06_GenerateProductTypeTaxonomy-SD_v1",
    "dataset_id": "aaae9cbd-92a3-4642-809e-c53f4eec5168",
    "dataset_name": "M06_V2_GenerateProductTypeTaxonomy",
    "prompt_id": "ee5bb5ac-b613-4579-b462-a9b61455d34b",
    "prompt_version_id": "1000196486895942787",
    "temperature": 0,
    "created": "2026-01-14 17:32:51.387000+00:00"
  },
  {
    "data_source": "M07_ExtractProductAttributes_gd1_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m07_gd",
    "pass_rate": 75.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m07_gd_judge_20260120_005734",
    "summary": {
      "error": 0,
      "fail": 10,
      "pass": 30
    },
    "timestamp": "2026-01-20T00:57:34.663211",
    "total_evaluations": 40,
    "braintrust_id": "a1086652-afcf-4ea5-aaf4-31fb888ae0e0",
    "braintrust_name": "M07_ExtractProductAttributes_gd_v1",
    "dataset_id": "27a50f6b-44da-4144-b897-85f4de1600b8",
    "dataset_name": "M07_ExtractProductAttributes_V1.1",
    "prompt_id": "d6da55ae-54fc-4706-9cbe-8e5636151372",
    "prompt_version_id": "1000196493521759930",
    "temperature": 0,
    "created": "2026-01-15 21:37:51.439000+00:00"
  },
  {
    "data_source": "M07_ExtractProductAttributes-sd1_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m07_sd",
    "pass_rate": 77.5,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m07_sd_judge_20260120_005857",
    "summary": {
      "error": 0,
      "fail": 9,
      "pass": 31
    },
    "timestamp": "2026-01-20T00:58:57.315491",
    "total_evaluations": 40,
    "braintrust_id": "7e1412bd-2304-4b3a-95b7-4ddbfbef6961",
    "braintrust_name": "M07_ExtractProductAttributes-SD1_v1",
    "dataset_id": "8d3adb98-a8bc-4bed-9162-b79a94dc238c",
    "dataset_name": "M07_V2_ExtractProductAttributes",
    "prompt_id": "c10225d0-4dbf-4b7d-8daa-80124142fdca",
    "prompt_version_id": "1000196486904202773",
    "temperature": 0,
    "created": "2026-01-14 17:51:56.531000+00:00"
  },
  {
    "data_source": "M08_AssignAttributeRanks_v1_dg1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o",
    "module": "m08",
    "pass_rate": 5.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m08_judge_20260120_010035",
    "summary": {
      "error": 0,
      "fail": 38,
      "pass": 2
    },
    "timestamp": "2026-01-20T01:00:35.082566",
    "total_evaluations": 40,
    "note": "REMOVED m08_sd - invalid data (contained M07 module data)",
    "braintrust_id": "be61b01a-7ec1-441a-a767-c839302022b2",
    "braintrust_name": "M08_AssignAttributeRanks-6d9e5ce6",
    "dataset_id": "5c325eb0-6e7d-4b25-bee0-6847fc4ce263",
    "dataset_name": "M08_AssignAttributeRanks_V1.1",
    "prompt_id": "992eaa83-fd62-4308-a31e-d7543b6c0742",
    "prompt_version_id": "1000196486131603668",
    "temperature": 0,
    "created": "2026-01-14 14:18:03.930000+00:00"
  },
  {
    "data_source": "M08_V2_AssignAttributeRanks_v1_gd1_150126_1.csv",
    "dataset_version": "v2",
    "match_rate": 0,
    "model": "gpt-4o",
    "module": "m08_v2",
    "pass_rate": 7.5,
    "prompt_version": "v2",
    "rubrics_version": "v5",
    "run_id": "m08_v2_judge_20260120_010415",
    "summary": {
      "error": 0,
      "fail": 37,
      "pass": 3
    },
    "timestamp": "2026-01-20T01:04:15.956521",
    "total_evaluations": 40,
    "braintrust_id": "0ef768c9-04dd-45b6-a6d3-d3a33f763d63",
    "braintrust_name": "M08_V2_AssignAttributeRanks_v1",
    "dataset_id": "5c325eb0-6e7d-4b25-bee0-6847fc4ce263",
    "dataset_name": "M08_AssignAttributeRanks_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 20:36:55.613000+00:00"
  },
  {
    "data_source": "M08_V2_AssignAttributeRanks_sd1_v1_150126_1.csv",
    "dataset_version": "v2",
    "match_rate": 0,
    "model": "gpt-4o",
    "module": "m08_v2_sd",
    "pass_rate": 52.5,
    "prompt_version": "v2",
    "rubrics_version": "v5",
    "run_id": "m08_v2_sd_judge_20260120_010557",
    "summary": {
      "error": 0,
      "fail": 19,
      "pass": 21
    },
    "timestamp": "2026-01-20T01:05:57.604187",
    "total_evaluations": 40,
    "braintrust_id": "e7eeca50-cb96-4276-ac15-cb50420d2341",
    "braintrust_name": "M08_V2_AssignAttributeRanks-sd1_v1",
    "dataset_id": "08dd82c4-6e93-4eaa-8612-5e727dd404e9",
    "dataset_name": "M08_SD1_AssignAttributeRanks",
    "prompt_id": "e632d218-b335-47ac-aba4-5f80864981f3",
    "prompt_version_id": "1000196487582052816",
    "temperature": 0,
    "created": "2026-01-14 20:54:53.936000+00:00"
  },
  {
    "data_source": "M09_IdentifyPrimaryIntendedUse_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m09",
    "pass_rate": 62.5,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m09_judge_20260120_010658",
    "summary": {
      "error": 0,
      "fail": 15,
      "pass": 25
    },
    "timestamp": "2026-01-20T01:06:58.509576",
    "total_evaluations": 40,
    "braintrust_id": "273035ae-7b24-4cd5-92f2-eab70c66c836",
    "braintrust_name": "M09_IdentifyPrimaryIntendedUse_V1.1",
    "dataset_id": "a8fdb7f3-c58e-4bc0-8153-a58cd50c8bc6",
    "dataset_name": "M09_IdentifyPrimaryIntendedUse_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 21:45:34.554000+00:00"
  },
  {
    "data_source": "M10_ValidatePrimaryIntendedUse_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m10",
    "pass_rate": 20.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m10_judge_20260120_010748",
    "summary": {
      "error": 0,
      "fail": 16,
      "pass": 4
    },
    "timestamp": "2026-01-20T01:07:48.837867",
    "total_evaluations": 20,
    "braintrust_id": "1f3b3531-a143-4195-88c5-a91458cf9d03",
    "braintrust_name": "M10_ValidatePrimaryIntendedUse_V1.1_v1",
    "dataset_id": "329287b2-4ebd-472c-8db3-f7e731cc56e7",
    "dataset_name": "M10_ValidatePrimaryIntendedUse_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 21:46:50.968000+00:00"
  },
  {
    "data_source": "M11_IdentifyHardConstraints_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m11",
    "pass_rate": 52.9,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m11_judge_20260120_011020",
    "summary": {
      "error": 0,
      "fail": 33,
      "pass": 37
    },
    "timestamp": "2026-01-20T01:10:20.800444",
    "total_evaluations": 70,
    "braintrust_id": "e94e9edc-22af-48c5-b151-ba9af6dc2996",
    "braintrust_name": "M11_IdentifyHardConstraints_V1.1_v1",
    "dataset_id": "7f15bfc1-4541-4652-a667-bb1842b43e46",
    "dataset_name": "M11_IdentifyHardConstraints_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 22:15:16.479000+00:00"
  },
  {
    "data_source": "M12_HardConstraintViolationCheck_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m12",
    "pass_rate": 60.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m12_judge_20260120_011056",
    "summary": {
      "error": 0,
      "fail": 8,
      "pass": 12
    },
    "timestamp": "2026-01-20T01:10:56.991676",
    "total_evaluations": 20,
    "braintrust_id": "f880cfd8-af50-4a71-8e66-90311a9a64a8",
    "braintrust_name": "M12_HardConstraintViolationCheck_v1_20260115_1",
    "dataset_id": "cf2c2974-09d6-41b7-93b1-272d3c7e2716",
    "dataset_name": "M12_CheckHardConstraint_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-16 07:59:20.368000+00:00"
  },
  {
    "data_source": "M13_ProductTypeCheck_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m13",
    "pass_rate": 90.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m13_judge_20260120_011158",
    "summary": {
      "error": 0,
      "fail": 3,
      "pass": 27
    },
    "timestamp": "2026-01-20T01:11:58.977590",
    "total_evaluations": 30,
    "braintrust_id": "f02822df-b216-43a8-bb07-eacdc90f2ed3",
    "braintrust_name": "M13_ProductTypeCheck_V1.1_v1",
    "dataset_id": "25532e83-5425-401e-9a3a-50782d574776",
    "dataset_name": "M13_CheckProductType_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 22:23:42.797000+00:00"
  },
  {
    "data_source": "M14_PrimaryUseCheckSameType_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m14",
    "pass_rate": 100.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m14_judge_20260120_011314",
    "summary": {
      "error": 0,
      "fail": 0,
      "pass": 30
    },
    "timestamp": "2026-01-20T01:13:14.384437",
    "total_evaluations": 30,
    "braintrust_id": "9bec004e-4a1c-4df7-b7b4-23d13e8973e5",
    "braintrust_name": "M14_PrimaryUseCheckSameType_V1.1_v1",
    "dataset_id": "498ae6c2-1bfa-44a3-9948-889856d6d796",
    "dataset_name": "M14_CheckPrimaryUseSameType_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 22:26:24.937000+00:00"
  },
  {
    "data_source": "M15_SubstituteCheck_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m15",
    "pass_rate": 95.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m15_judge_20260120_011405",
    "summary": {
      "error": 0,
      "fail": 1,
      "pass": 19
    },
    "timestamp": "2026-01-20T01:14:05.532752",
    "total_evaluations": 20,
    "braintrust_id": "20ad9832-cec0-4e7c-96de-70984a9b7976",
    "braintrust_name": "M15_SubstituteCheck_V1.1_v1",
    "dataset_id": "48c73d5b-c15c-4e63-ae61-fb040bf65543",
    "dataset_name": "M15_CheckSubstitute_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 22:28:58.660000+00:00"
  },
  {
    "data_source": "M16_ComplementaryCheck_v1_150126_1.csv",
    "dataset_version": null,
    "match_rate": 0,
    "model": "gpt-4o-mini",
    "module": "m16",
    "pass_rate": 75.0,
    "prompt_version": "v1",
    "rubrics_version": "v5",
    "run_id": "m16_judge_20260120_011538",
    "summary": {
      "error": 0,
      "fail": 10,
      "pass": 30
    },
    "timestamp": "2026-01-20T01:15:38.333262",
    "total_evaluations": 40,
    "braintrust_id": "12b05ae7-e0c4-48c8-a7bb-e07b3cc1b95a",
    "braintrust_name": "M16_ComplementaryCheck_V1.1_v1",
    "dataset_id": "af991abf-dce7-4155-b279-6b98cae77f86",
    "dataset_name": "M16_CheckComplementary_V1.1",
    "prompt_id": null,
    "prompt_version_id": null,
    "temperature": 0,
    "created": "2026-01-15 22:31:40.360000+00:00"
  }
];

const suggestionsData = [
  {
    "rubric": "No Hallucinated Brand",
    "criticality": "High",
    "passRate": 60.0,
    "issueType": "Model Issue + Prompt Clarity",
    "analysisSummary": "Model extracts 'Vibe' as standalone sub-brand from 'Vibe Beam' when prompt says to skip entire sub-brand if last word is generic",
    "detailedSuggestion": "PROMPT FIX: Add explicit rule for sub-brand handling",
    "promptChange": "Add: 'If sub-brand fails Amazon Test, skip ENTIRE sub-brand'",
    "impact": "Expected to improve from 60% to 90%+ for this rubric",
    "validated": false,
    "module": "M01"
  },
  {
    "rubric": "No Product Words in Brand",
    "criticality": "Medium",
    "passRate": 86.7,
    "issueType": "Model Issue",
    "analysisSummary": "AirPods being extracted as brand entity when it's a product word",
    "detailedSuggestion": "Add AirPods, iPhone, iPad to product words exclusion list",
    "validated": false,
    "module": "M01"
  },
  {
    "rubric": "No Duplicate Entities",
    "criticality": "Medium",
    "passRate": 86.7,
    "issueType": "Model Issue",
    "analysisSummary": "Some outputs contain exact duplicate strings",
    "detailedSuggestion": "Strengthen final duplicate validation step",
    "validated": false,
    "module": "M01"
  },
  {
    "rubric": "8-12 Variations Generated",
    "criticality": "High",
    "passRate": 60.0,
    "issueType": "Model Issue",
    "analysisSummary": "4 of 10 samples fail due to DUPLICATE variations",
    "detailedSuggestion": "Add explicit duplicate validation step",
    "validated": true,
    "module": "M01A"
  },
  {
    "rubric": "No Unrelated Terms",
    "criticality": "Low",
    "passRate": 90.0,
    "issueType": "Judge Issue",
    "analysisSummary": "1 false positive - judge incorrectly flagged 'KichenAid' typo as unrelated",
    "detailedSuggestion": "Update rubric to clarify typos are valid variations",
    "validated": true,
    "module": "M01A"
  },
  {
    "rubric": "Correct CB/null Classification",
    "criticality": "Critical",
    "passRate": 33.3,
    "issueType": "Judge Issue (Data Quality)",
    "analysisSummary": "9 of 10 failures are DATA ISSUES - model correctly returned null, dataset is wrong",
    "detailedSuggestion": "DATA FIX: Update dataset expected values. Change from 'CB' to null for brands not in list",
    "validated": true,
    "module": "M04"
  },
  {
    "rubric": "Taxonomy Generated",
    "criticality": "Medium",
    "passRate": 65.0,
    "issueType": "Model Issue",
    "analysisSummary": "Taxonomy sometimes too generic or misses key product types",
    "validated": false,
    "module": "M06"
  },
  {
    "rubric": "Ranks Assigned",
    "criticality": "Critical",
    "passRate": 5.0,
    "issueType": "Judge Issue + Model Issue",
    "analysisSummary": "Judge expects 'Use Case' but prompt shows 'UseCase'. Model also skips ranking some attributes.",
    "specificIssue": "Prompt CLEARLY shows 'UseCase' (no space) in all examples, but judge fails because expected values have 'Use Case' (with space)",
    "detailedSuggestion": "FIX 1 (JUDGE): Update expected values to 'UseCase'. FIX 2 (MODEL): Add 'rank EVERY attribute' instruction",
    "impact": "Expected to improve from 5% to 70%+ after fixing both issues",
    "validated": true,
    "module": "M08"
  },
  {
    "rubric": "Title Attributes Ranked 1-2",
    "criticality": "High",
    "passRate": 10.0,
    "issueType": "Model Issue",
    "analysisSummary": "Title attributes sometimes ranked 3+ instead of required 1-2",
    "detailedSuggestion": "Emphasize title attribute priority in prompt",
    "validated": false,
    "module": "M08"
  },
  {
    "rubric": "Primary Use Identified",
    "criticality": "Medium",
    "passRate": 62.5,
    "issueType": "Model Issue + Data Issue",
    "analysisSummary": "Model identifies correct use but phrasing doesn't match expected exactly",
    "validated": false,
    "module": "M09"
  },
  {
    "rubric": "Invalid M09 Output Flagged",
    "criticality": "Critical",
    "passRate": 20.0,
    "issueType": "Judge Issue (Strict Matching)",
    "analysisSummary": "Judge fails because model output is semantically equivalent but not exact string match",
    "specificIssue": "Expected: 'Listening to audio'. Model: 'Wireless music and audio listening'. Both describe same use case!",
    "detailedSuggestion": "Allow semantic equivalence in primary use comparison",
    "rubricChange": "Add: 'Semantically equivalent uses are acceptable: Listening to audio = Wireless music listening'",
    "impact": "Expected to improve from 20% to 80%+ if semantic matching allowed",
    "validated": true,
    "module": "M10"
  },
  {
    "rubric": "Constraints Are Product-Specific",
    "criticality": "Medium",
    "passRate": 40.0,
    "issueType": "Model Issue",
    "analysisSummary": "Model sometimes includes generic constraints instead of product-specific ones",
    "detailedSuggestion": "Add explicit examples of what is NOT a hard constraint",
    "validated": false,
    "module": "M11"
  },
  {
    "rubric": "Complementary Correctly Identified",
    "criticality": "Medium",
    "passRate": 75.0,
    "issueType": "Model Issue",
    "analysisSummary": "Some complementary relationships not identified correctly",
    "validated": false,
    "module": "M16"
  }
];

const appliedData = {
  "version": "1.0",
  "last_updated": "2026-01-19",
  "prompt_versions": {
    "M01": {
      "v1": {
        "file": "m01_extract_own_brand_entities.md",
        "date": "2026-01-15",
        "description": "Initial version - baseline prompt",
        "applied_suggestions": [],
        "pass_rate": 30.0,
        "model": "gpt-4o",
        "rubric_summary": {
          "Brand Extracted": "10.0%",
          "No Hallucinated Brand": "20.0%",
          "No Product Words": "70.0%",
          "Amazon Test Applied": "10.0%",
          "No Duplicates": "40.0%"
        }
      },
      "v2": {
        "file": "m01_v2_extract_own_brand_entities.md",
        "date": "2026-01-19",
        "description": "Added brand extraction patterns and Amazon Test instructions",
        "applied_suggestions": [
          {
            "id": "M01_SUG_001",
            "rubric": "Brand Extracted",
            "suggestion_summary": "Added explicit brand extraction patterns",
            "status": "APPLIED"
          },
          {
            "id": "M01_SUG_002",
            "rubric": "Amazon Test Applied",
            "suggestion_summary": "Added step-by-step Amazon Test instructions",
            "status": "APPLIED"
          }
        ],
        "pass_rate": 45.0,
        "model": "gpt-4o",
        "improvement": "+15%",
        "rubric_summary": {
          "Brand Extracted": "30.0%",
          "No Hallucinated Brand": "40.0%",
          "No Product Words": "65.0%",
          "Amazon Test Applied": "25.0%",
          "No Duplicates": "65.0%"
        }
      },
      "v3": {
        "file": "m01_v3_extract_own_brand_entities.md",
        "date": "2026-01-19",
        "description": "Major improvements based on evaluation feedback",
        "applied_suggestions": [
          {
            "id": "M01_SUG_001",
            "rubric": "No Hallucinated Brand",
            "suggestion_summary": "Skip ENTIRE sub-brand when last word is generic",
            "prompt_change": "Added section \"\ud83d\udeab DO NOT Extract Partial Sub-Brands\":\n- When multi-word sub-brand fails Amazon Test, skip ENTIRE concept\n- Example: \"Sound Pro\" \u2192 \"pro\" is generic \u2192 skip both words, NOT just \"Pro\"\n- Only extract main brand (e.g., \"Bose\")\n",
            "expected_impact": "60% \u2192 90%+ for No Hallucinated Brand rubric",
            "status": "APPLIED"
          },
          {
            "id": "M01_SUG_002",
            "rubric": "Brand Extracted",
            "suggestion_summary": "Handle multi-word brand names like 'Hydro Flask'",
            "prompt_change": "Added section \"Handle Multi-Word Brand Names\":\n- Extract full form: \"Hydro Flask\", \"hydro flask\"\n- Extract merged: \"HydroFlask\", \"hydroflask\"\n- Extract first word: \"Hydro\", \"hydro\"\n- Apply typos to merged and first word\n",
            "expected_impact": "Better coverage for multi-word brands",
            "status": "APPLIED"
          }
        ],
        "pass_rate": 57.3,
        "model": "gpt-4o-mini",
        "improvement": "+12.3%",
        "rubric_summary": {
          "Brand Extracted": "60.0%",
          "No Hallucinated Brand": "53.3%",
          "No Product Words": "80.0%",
          "Amazon Test Applied": "46.7%",
          "No Duplicates": "46.7%"
        }
      },
      "v4": {
        "file": "m01_v4_extract_own_brand_entities.md",
        "date": "2026-01-21",
        "description": "Refined brand scope handling and OB vs CB clarity",
        "applied_suggestions": [
          {
            "id": "M01_SUG_005",
            "rubric": "Brand Scope",
            "suggestion_summary": "Clarify OB vs CB classification with stronger examples",
            "prompt_change": "Added explicit criteria for brand ownership scope determination",
            "expected_impact": "Improved brand scope accuracy",
            "status": "APPLIED"
          }
        ],
        "pass_rate": 53.7,
        "model": "gpt-4o",
        "match_rate": 77.8,
        "improvement": "+8.7%",
        "rubric_summary": {
          "Brand Extracted": "77.8%",
          "No Hallucinated Brand": "55.6%",
          "No Product Words": "55.6%",
          "Amazon Test Applied": "41.4%",
          "No Duplicates": "38.4%"
        }
      },
      "v5": {
        "file": "m01_v5_extract_own_brand_entities.md",
        "date": "2026-01-21",
        "description": "Further refinements based on v4 error analysis",
        "applied_suggestions": [
          {
            "id": "M01_SUG_006",
            "rubric": "Brand Extracted",
            "suggestion_summary": "Improved edge case handling for complex brand names",
            "prompt_change": "Enhanced brand extraction logic for edge cases",
            "expected_impact": "Better coverage for complex brands",
            "status": "APPLIED"
          }
        ],
        "pass_rate": 58.4,
        "model": "gpt-4o-mini",
        "match_rate": 73.7,
        "improvement": "+4.7%",
        "rubric_summary": {
          "Brand Extracted": "73.7%",
          "No Hallucinated Brand": "63.6%",
          "No Product Words": "75.8%",
          "Amazon Test Applied": "46.5%",
          "No Duplicates": "32.3%"
        }
      }
    }
  },
  "pending_suggestions": {
    "M01": [
      {
        "id": "M01_SUG_003",
        "rubric": "No Product Words in Brand",
        "suggestion": "Add AirPods, iPhone, iPad to product words exclusion list",
        "status": "PROPOSED",
        "priority": "Medium"
      },
      {
        "id": "M01_SUG_004",
        "rubric": "No Duplicate Entities",
        "suggestion": "Add explicit character-by-character duplicate check instruction",
        "status": "PROPOSED",
        "priority": "Medium"
      }
    ],
    "M04": [
      {
        "id": "M04_SUG_001",
        "rubric": "Correct CB/null Classification",
        "suggestion": "Fix dataset - brands not in competitor_entities should expect null",
        "status": "DATA_FIX_NEEDED",
        "priority": "Critical",
        "affected_keywords": [
          "oven mitts oxo",
          "blue q oven mitt",
          "sur la table oven mitts",
          "pioneer woman oven mitts",
          "cuisinart oven mitts"
        ]
      }
    ]
  },
  "impact_summary": {
    "M01": {
      "baseline": 30.0,
      "current": 58.4,
      "improvement": 28.4,
      "applied_count": 4,
      "pending_count": 2,
      "best_version": "v5",
      "best_model": "gpt-4o-mini",
      "best_match_rate": 73.7,
      "notes": "V5 with gpt-4o-mini achieves best pass rate (58.4%) and good match rate (73.7%)"
    },
    "M04": {
      "baseline": 43.3,
      "current": 60.0,
      "improvement": 16.7,
      "applied_count": 0,
      "pending_count": 1,
      "notes": "Improvement from model upgrade (gpt-4o-mini \u2192 gpt-4o), not prompt changes"
    }
  }
};

const improvementHistory = {
  "version": "1.0",
  "last_updated": "2026-01-20",
  "modules": {
    "M01": {
      "versions": {
        "v1": {
          "evaluation": {
            "date": "2026-01-20",
            "pass_rate": 30.0,
            "model": "gpt-4o",
            "data_source": "M01_ExtractOwnBrandEntities_v1_150126_1.csv",
            "rubric_breakdown": {
              "Brand Extracted": "10.0%",
              "No Hallucinated Brand": "20.0%",
              "No Product Words in Brand": "70.0%",
              "Amazon Test Applied": "10.0%",
              "No Duplicate Entities": "40.0%"
            }
          },
          "suggestions": [
            {
              "rubric": "Brand Extracted",
              "issue": "Only 10% pass rate - model misses brand variations and sub-brands",
              "suggestion": "Add explicit examples of brand extraction patterns",
              "priority": "high",
              "status": "applied",
              "applied_in": "v2"
            },
            {
              "rubric": "Amazon Test Applied",
              "issue": "Only 10% pass rate - model doesn't consistently apply Amazon search test",
              "suggestion": "Add step-by-step Amazon Test instructions",
              "priority": "high",
              "status": "applied",
              "applied_in": "v2"
            }
          ]
        },
        "v2": {
          "evaluation": {
            "date": "2026-01-20",
            "pass_rate": 45.0,
            "model": "gpt-4o",
            "data_source": "M01_ExtractOwnBrandEntities_v2_190126_1.csv",
            "rubric_breakdown": {
              "Brand Extracted": "30.0%",
              "No Hallucinated Brand": "40.0%",
              "No Product Words in Brand": "65.0%",
              "Amazon Test Applied": "25.0%",
              "No Duplicate Entities": "65.0%"
            }
          },
          "applied_from_v1": [
            "Added explicit examples of brand extraction patterns",
            "Added step-by-step Amazon Test instructions"
          ],
          "improvement_vs_previous": "+15%",
          "suggestions": [
            {
              "rubric": "No Hallucinated Brand",
              "issue": "40% pass - Model extracts manufacturer as brand (Resolve Designs vs Rx Crush)",
              "suggestion": "Add rule: manufacturer ≠ brand unless it appears in title",
              "priority": "high",
              "status": "applied",
              "applied_in": "v3"
            },
            {
              "rubric": "Brand Extracted",
              "issue": "30% pass - Still missing many brand variations",
              "suggestion": "Add more comprehensive variation examples",
              "priority": "high",
              "status": "applied",
              "applied_in": "v3"
            }
          ]
        },
        "v3": {
          "evaluation": {
            "date": "2026-01-20",
            "pass_rate": 57.3,
            "model": "gpt-4o-mini",
            "data_source": "M01_V2_ExtractOwnBrandEntities_v3_190126_1.csv",
            "rubric_breakdown": {
              "Brand Extracted": "60.0%",
              "No Hallucinated Brand": "53.3%",
              "No Product Words in Brand": "80.0%",
              "Amazon Test Applied": "46.7%",
              "No Duplicate Entities": "46.7%"
            }
          },
          "applied_from_v2": [
            "Added manufacturer vs brand distinction rule",
            "Expanded brand variation examples"
          ],
          "improvement_vs_previous": "+12.3%",
          "suggestions": [
            {
              "rubric": "No Hallucinated Brand",
              "issue": "53% pass - Still extracting some invalid sub-brands",
              "suggestion": "Strengthen sub-brand validation rules",
              "priority": "high",
              "status": "applied",
              "applied_in": "v4"
            },
            {
              "rubric": "No Duplicate Entities",
              "issue": "46.7% pass - Duplicate variations appearing",
              "suggestion": "Add deduplication step before output",
              "priority": "medium",
              "status": "applied",
              "applied_in": "v4"
            }
          ]
        },
        "v4": {
          "evaluation": {
            "date": "2026-01-21",
            "pass_rate": 53.7,
            "model": "gpt-4o",
            "data_source": "M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4o.csv",
            "match_rate": 77.8,
            "rubric_breakdown": {
              "Brand Extracted": "77.8%",
              "No Hallucinated Brand": "55.6%",
              "No Product Words in Brand": "55.6%",
              "Amazon Test Applied": "41.4%",
              "No Duplicate Entities": "38.4%"
            }
          },
          "applied_from_v3": [
            "Refined brand scope handling (OB vs CB)",
            "Added sub-brand validation improvements"
          ],
          "improvement_vs_previous": "-3.6% pass rate but +17.8% Brand Extracted",
          "note": "V4 with gpt-4o achieves BEST Brand Extracted at 77.8%",
          "suggestions": [
            {
              "rubric": "No Duplicate Entities",
              "issue": "38.4% pass - Duplicates regressed significantly",
              "suggestion": "Add explicit deduplication in output formatting",
              "priority": "high",
              "status": "applied",
              "applied_in": "v5"
            },
            {
              "rubric": "Amazon Test Applied",
              "issue": "41.4% pass - Needs improvement",
              "suggestion": "Strengthen Amazon Test application",
              "priority": "medium",
              "status": "applied",
              "applied_in": "v5"
            }
          ]
        },
        "v4_gpt4omini": {
          "evaluation": {
            "date": "2026-01-21",
            "pass_rate": 40.2,
            "model": "gpt-4o-mini",
            "data_source": "M01_V4_ExtractOwnBrandEntities_v4_210126_gpt4omini.csv",
            "match_rate": 64.6,
            "rubric_breakdown": {
              "Brand Extracted": "64.6%",
              "No Hallucinated Brand": "41.4%",
              "No Product Words in Brand": "44.4%",
              "Amazon Test Applied": "24.2%",
              "No Duplicate Entities": "26.3%"
            }
          },
          "note": "V4 with gpt-4o-mini shows lower performance than gpt-4o across all rubrics."
        },
        "v5": {
          "evaluation": {
            "date": "2026-01-21",
            "pass_rate": 58.4,
            "model": "gpt-4o-mini",
            "data_source": "M01_V5_ExtractOwnBrandEntities_v5_210126_gpt4omini.csv",
            "match_rate": 73.7,
            "rubric_breakdown": {
              "Brand Extracted": "73.7%",
              "No Hallucinated Brand": "63.6%",
              "No Product Words in Brand": "75.8%",
              "Amazon Test Applied": "46.5%",
              "No Duplicate Entities": "32.3%"
            }
          },
          "applied_from_v4": [
            "Added explicit deduplication in output",
            "Strengthened Amazon Test application",
            "Improved product word filtering"
          ],
          "improvement_vs_previous": "+18.2% vs v4 gpt-4o-mini",
          "note": "V5 is BEST overall version: 58.4% pass rate with gpt-4o-mini",
          "suggestions": [
            {
              "rubric": "No Duplicate Entities",
              "issue": "32.3% pass - Still lowest performing rubric",
              "suggestion": "Implement stricter deduplication logic",
              "priority": "high",
              "status": "pending"
            },
            {
              "rubric": "Amazon Test Applied",
              "issue": "46.5% pass - Room for improvement",
              "suggestion": "Add more Amazon Test examples",
              "priority": "medium",
              "status": "pending"
            }
          ]
        },
        "v5_gpt5": {
          "evaluation": {
            "date": "2026-01-21",
            "pass_rate": 48.7,
            "model": "gpt-5",
            "data_source": "M01_V5_ExtractOwnBrandEntities_v5_210126_gpt5.csv",
            "match_rate": 45.5,
            "rubric_breakdown": {
              "Brand Extracted": "46.5%",
              "No Hallucinated Brand": "41.4%",
              "No Product Words in Brand": "60.6%",
              "Amazon Test Applied": "35.4%",
              "No Duplicate Entities": "59.6%"
            }
          },
          "note": "V5 with gpt-5 shows lower performance than gpt-4o-mini (-9.7% pass rate), but better deduplication (59.6% vs 32.3%)."
        }
      }
    },
    "M01A": {
      "versions": {
        "v1": {
          "evaluation": {
            "date": "2026-01-19",
            "pass_rate": 90.0,
            "model": "gpt-4o-mini",
            "data_source": "M01A_ExtractOwnBrandVariations_v1_150126_1.csv"
          },
          "suggestions": [
            {
              "rubric": "Variations Generated",
              "issue": "Some edge cases missed",
              "suggestion": "Add more typo patterns",
              "priority": "low",
              "status": "applied",
              "applied_in": "v2"
            }
          ]
        },
        "v2": {
          "evaluation": {
            "date": "2026-01-20",
            "pass_rate": 85.0,
            "model": "gpt-5",
            "data_source": "M01A_V2_ExtractOwnBrandVariations_v2_190126_gpt5.csv"
          },
          "applied_from_v1": [
            "Added more typo patterns"
          ],
          "improvement_vs_previous": "-5%",
          "note": "Regression with gpt-5, may need prompt adjustment",
          "suggestions": [
            {
              "rubric": "No Duplicates",
              "issue": "GPT-5 generates some duplicates",
              "suggestion": "Add explicit deduplication instruction",
              "priority": "medium",
              "status": "pending"
            }
          ]
        }
      }
    }
  }
};
// Binary classification metrics for classifier modules
const binaryMetrics = {
  "m02": {
    "tp": 97,
    "tn": 735,
    "fp": 4,
    "fn": 80,
    "total": 916,
    "accuracy": 90.8,
    "precision": 96.0,
    "recall": 54.8,
    "f1": 69.8,
    "mcc": 0.684,
    "skipped": 0,
    "labels": {
      "tp": "OB",
      "tn": "Null",
      "fp": "Null\u2192OB",
      "fn": "OB\u2192Null"
    }
  },
  "m02b": {
    "tp": 97,
    "tn": 739,
    "fp": 0,
    "fn": 80,
    "total": 916,
    "accuracy": 91.3,
    "precision": 100.0,
    "recall": 54.8,
    "f1": 70.8,
    "mcc": 0.703,
    "skipped": 0,
    "labels": {
      "tp": "OB",
      "tn": "Null",
      "fp": "Null\u2192OB",
      "fn": "OB\u2192Null"
    }
  },
  "m04": {
    "tp": 156,
    "tn": 1443,
    "fp": 36,
    "fn": 124,
    "total": 1759,
    "accuracy": 90.9,
    "precision": 81.2,
    "recall": 55.7,
    "f1": 66.1,
    "mcc": 0.625,
    "skipped": 0,
    "labels": {
      "tp": "CB",
      "tn": "Null",
      "fp": "Null\u2192CB",
      "fn": "CB\u2192Null"
    }
  },
  "m04b": {
    "tp": 67,
    "tn": 1477,
    "fp": 5,
    "fn": 210,
    "total": 1759,
    "accuracy": 87.8,
    "precision": 93.1,
    "recall": 24.2,
    "f1": 38.4,
    "mcc": 0.438,
    "skipped": 0,
    "labels": {
      "tp": "CB",
      "tn": "Null",
      "fp": "Null\u2192CB",
      "fn": "CB\u2192Null"
    }
  },
  "m05": {
    "tp": 1414,
    "tn": 249,
    "fp": 81,
    "fn": 15,
    "total": 1759,
    "accuracy": 94.5,
    "precision": 94.6,
    "recall": 99.0,
    "f1": 96.7,
    "mcc": 0.813,
    "skipped": 0,
    "labels": {
      "tp": "NB",
      "tn": "Branded",
      "fp": "Brand\u2192NB",
      "fn": "NB\u2192Brand"
    }
  },
  "m05b": {
    "tp": 1400,
    "tn": 273,
    "fp": 57,
    "fn": 29,
    "total": 1759,
    "accuracy": 95.1,
    "precision": 96.1,
    "recall": 98.0,
    "f1": 97.0,
    "mcc": 0.835,
    "skipped": 0,
    "labels": {
      "tp": "NB",
      "tn": "Branded",
      "fp": "Brand\u2192NB",
      "fn": "NB\u2192Brand"
    }
  },
  "m12": {
    "tp": 4,
    "tn": 429,
    "fp": 9,
    "fn": 0,
    "total": 442,
    "accuracy": 98.0,
    "precision": 30.8,
    "recall": 100.0,
    "f1": 47.1,
    "mcc": 0.549,
    "skipped": 0,
    "labels": {
      "tp": "Violates",
      "tn": "OK",
      "fp": "OK\u2192Violates",
      "fn": "Violates\u2192OK"
    }
  },
  "m13": {
    "tp": 195,
    "tn": 182,
    "fp": 28,
    "fn": 33,
    "total": 438,
    "accuracy": 86.1,
    "precision": 87.4,
    "recall": 85.5,
    "f1": 86.5,
    "mcc": 0.721,
    "skipped": 0,
    "labels": {
      "tp": "Match",
      "tn": "Diff",
      "fp": "Diff\u2192Match",
      "fn": "Match\u2192Diff"
    }
  },
  "m14": {
    "tp": 215,
    "tn": 0,
    "fp": 0,
    "fn": 13,
    "total": 228,
    "accuracy": 94.3,
    "precision": 100.0,
    "recall": 94.3,
    "f1": 97.1,
    "mcc": 0,
    "skipped": 0,
    "labels": {
      "tp": "R",
      "tn": "-",
      "fp": "-",
      "fn": "R\u2192Other"
    },
    "note": "All expected=R"
  },
  "m15": {
    "tp": 11,
    "tn": 170,
    "fp": 9,
    "fn": 20,
    "total": 210,
    "accuracy": 86.2,
    "precision": 55.0,
    "recall": 35.5,
    "f1": 43.1,
    "mcc": 0.368,
    "skipped": 0,
    "labels": {
      "tp": "S",
      "tn": "not-S",
      "fp": "null\u2192S",
      "fn": "S\u2192not-S"
    }
  },
  "m16": {
    "tp": 135,
    "tn": 0,
    "fp": 0,
    "fn": 44,
    "total": 179,
    "accuracy": 75.4,
    "precision": 100.0,
    "recall": 75.4,
    "f1": 86.0,
    "mcc": 0,
    "skipped": 0,
    "labels": {
      "tp": "C",
      "tn": "-",
      "fp": "-",
      "fn": "C\u2192N"
    },
    "note": "Expected=C, outputs C or N"
  }
};