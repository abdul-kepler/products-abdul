# Complete Brand Scope Classification Errors

> Full list of all FP and FN errors with reasoning
> Generated: 2026-01-21

====================================================================================================
# M02
====================================================================================================

## M02 FALSE POSITIVES (FP): 4 errors

### FP #1
**Keyword:** `ironflask 40 oz`
**Expected:** null
**Model Output:** OB
**Reasoning:** Verified: 'Owala' (o-w-a-l-a) found at position 0-5 in keyword 'ironflask 40 oz'.
**Context:** ['Owala', 'Owala FreeSip', 'FreeSip', 'Owala', 'Owalaa', 'Owallah', 'Ohwala', 'O wala', 'O-wala', 'Free Sip', 'Freesip', 'FreeSipp']

### FP #2
**Keyword:** `contingo`
**Expected:** null
**Model Output:** OB
**Reasoning:** Verified: 'Owala' (o-w-a-l-a) found in keyword 'contingo'.
**Context:** ['Owala', 'Owala FreeSip', 'FreeSip', 'Owala', 'Owalaa', 'Owallah', 'Ohwala', 'O wala', 'O-wala', 'Free Sip', 'Freesip', 'FreeSipp']

### FP #3
**Keyword:** `iton flask`
**Expected:** null
**Model Output:** OB
**Reasoning:** Verified: 'Owala' (o-w-a-l-a) found in 'iton flask'.
**Context:** ['Owala', 'Owala FreeSip', 'FreeSip', 'Owala', 'Owalaa', 'Owallah', 'Ohwala', 'O wala', 'O-wala', 'Free Sip', 'Freesip', 'FreeSipp']

### FP #4
**Keyword:** `iceflow`
**Expected:** null
**Model Output:** OB
**Reasoning:** Verified: 'Owala' (o-w-a-l-a) found in 'iceflow'.
**Context:** ['Owala', 'Owala FreeSip', 'FreeSip', 'Owala', 'Owalaa', 'Owallah', 'Ohwala', 'O wala', 'O-wala', 'Free Sip', 'Freesip', 'FreeSipp']

## M02 FALSE NEGATIVES (FN): 80 errors

### FN #1
**Keyword:** `helicopter transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'helicopter transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #2
**Keyword:** `windblade transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'windblade transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #3
**Keyword:** `jet fire transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'jet fire transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #4
**Keyword:** `starscreen transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'starscreen transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #5
**Keyword:** `astrotrain transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'astrotrain transformer toy'. The keyword is a generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #6
**Keyword:** `sunstreaker transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'sunstreaker transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #7
**Keyword:** `cheetor transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'cheetor transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #8
**Keyword:** `bludgeon transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bludgeon transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #9
**Keyword:** `scrooge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'scrooge transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #10
**Keyword:** `transformers figures`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformers figures'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #11
**Keyword:** `transformers action figures`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformers action figures'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #12
**Keyword:** `transformers toys`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformers toys'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #13
**Keyword:** `rx enfit syringe`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx enfit syringe'. Generic product search.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #14
**Keyword:** `rx cru syringes`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx cru syringes'. The keyword does not contain any of the specified brand entities.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #15
**Keyword:** `rx syringes`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx syringes'. The keyword is generic and does not contain any of the specified brand entities.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #16
**Keyword:** `syrings rx`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'syrings rx'. The keyword does not contain any of the specified brand entities as an exact substring.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #17
**Keyword:** `rx enfit syringe`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx enfit syringe'. Generic product search.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #18
**Keyword:** `rx cru syringes`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx cru syringes'. The keyword does not contain any of the specified brand entities.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #19
**Keyword:** `rx syringes`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rx syringes'. The keyword is generic and does not contain any of the specified brand entities.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #20
**Keyword:** `syrings rx`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'syrings rx'. The keyword does not contain any of the specified brand entities as an exact substring.
**Context:** ['Rx Crush', 'RxCrush', 'RX Crush', 'Rx crush', 'Rx-Crush', 'RXCrush', 'Rx Crushes', 'Rx Crusch', 'Rx Crushh']

### FN #21
**Keyword:** `Pineer jacket`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'Pineer jacket'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Pioneer Camp', 'PioneerCamp', 'Pionner Camp', 'Pioneer Camps', 'Pioner Camp', 'Pioneer Kamp']

### FN #22
**Keyword:** `Jikashu phone holder for gym`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: 'Jikasho' (j-i-k-a-s-h-o) not found in 'Jikashu phone holder for gym'.
**Context:** ['Jikasho', 'Jikaso', 'Jikasho', 'Jikashoo', 'Jikasho', 'Jikasho']

### FN #23
**Keyword:** `11 inch bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in '11 inch bumblebee transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #24
**Keyword:** `large transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'large transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #25
**Keyword:** `giant bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'giant bumblebee transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #26
**Keyword:** `bumblebee transformers kids toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumblebee transformers kids toy'. 'Transformers' is a brand, but it is not an exact substring match as 'bumblebee' is not part of the brand entity.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #27
**Keyword:** `transformer plush toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformer plush toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #28
**Keyword:** `perceptor transformer toy 86`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'perceptor transformer toy 86'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #29
**Keyword:** `green transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'green transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #30
**Keyword:** `alchemist prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'alchemist prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #31
**Keyword:** `ultra magnus transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'ultra magnus transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #32
**Keyword:** `cyclonus transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'cyclonus transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #33
**Keyword:** `car transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'car transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #34
**Keyword:** `pink transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'pink transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #35
**Keyword:** `galvatron transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'galvatron transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #36
**Keyword:** `soundwave transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'soundwave transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #37
**Keyword:** `unicorn transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'unicorn transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #38
**Keyword:** `lockdown transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'lockdown transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #39
**Keyword:** `magnetic car transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'magnetic car transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #40
**Keyword:** `monster truck transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'monster truck transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #41
**Keyword:** `transformer toy studio series`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformer toy studio series'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #42
**Keyword:** `football transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'football transformer toy'. The keyword is generic and does not contain any exact substring match to the brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #43
**Keyword:** `cyclone hawk transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'cyclone hawk transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #44
**Keyword:** `wheel jack transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'wheel jack transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #45
**Keyword:** `transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #46
**Keyword:** `sentinel prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'sentinel prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #47
**Keyword:** `bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumblebee transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #48
**Keyword:** `bumblebee transformers toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumblebee transformers toy'. 'bumblebee' is a character but not a brand entity in the provided list.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #49
**Keyword:** `bumble bee transforming toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumble bee transforming toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #50
**Keyword:** `centennial prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'centennial prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #51
**Keyword:** `barricade transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'barricade transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #52
**Keyword:** `bumble bee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumble bee transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #53
**Keyword:** `shockwave transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'shockwave transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #54
**Keyword:** `sideswipe transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'sideswipe transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #55
**Keyword:** `alpha trion transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'alpha trion transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #56
**Keyword:** `cliffjumper transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'cliffjumper transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #57
**Keyword:** `orion pax transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'orion pax transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #58
**Keyword:** `star scream transformers toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'star scream transformers toy'. The keyword is a generic product search and does not contain an exact substring match for any brand entity.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #59
**Keyword:** `bumble transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'bumble transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #60
**Keyword:** `starscream transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'starscream transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #61
**Keyword:** `megatron transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'megatron transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #62
**Keyword:** `ratchet transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'ratchet transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #63
**Keyword:** `transformer car toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'transformer car toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #64
**Keyword:** `scourge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'scourge transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #65
**Keyword:** `fire truck transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'fire truck transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #66
**Keyword:** `voice activated transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'voice activated transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #67
**Keyword:** `metroplex transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'metroplex transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #68
**Keyword:** `onyx prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'onyx prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #69
**Keyword:** `nemesis prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'nemesis prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #70
**Keyword:** `skurge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'skurge transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #71
**Keyword:** `rodimus prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rodimus prime transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #72
**Keyword:** `apelinq transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'apelinq transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #73
**Keyword:** `battletrap transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'battletrap transformer toy'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #74
**Keyword:** `iron hide transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'iron hide transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #75
**Keyword:** `rhinox transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'rhinox transformer toy'. The keyword does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #76
**Keyword:** `toy train transformer`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'toy train transformer'. Generic product search.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #77
**Keyword:** `jetfire transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'jetfire transformer toy'. The keyword is generic and does not contain any exact substring match to the provided brand entities.
**Context:** ['Transformers', 'Hasbro', 'Cyber Commander Series', 'Optimus Prime', 'Tranformers', 'Transformors', 'Transformer Toys', 'Optimus Primee', 'Optimus Prine', 'OptimusPrime', 'Cyber Commander', 'Cyber Co

### FN #78
**Keyword:** `cisiky kitchen sink caddy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: 'Cisily' (c-i-s-i-l-y) not found in 'cisiky kitchen sink caddy'. No brand entity found.
**Context:** ['Cisily', 'CISILY', 'Cisly', 'Cisiliy', 'Cisely', 'Sisily', 'Cis ily', 'Cis-ily']

### FN #79
**Keyword:** `cicely kitchen sink caddy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: No brand entity found in 'cicely kitchen sink caddy'. The keyword does not contain any of the specified brand entities as an exact substring.
**Context:** ['Cisily', 'CISILY', 'Cisly', 'Cisiliy', 'Cisely', 'Sisily', 'Cis ily', 'Cis-ily']

### FN #80
**Keyword:** `cicily kitchen sink caddy`
**Expected:** OB
**Model Output:** null
**Reasoning:** Verified: 'Cisily' (c-i-s-i-l-y) not found in 'cicily kitchen sink caddy'.
**Context:** ['Cisily', 'CISILY', 'Cisly', 'Cisiliy', 'Cisely', 'Sisily', 'Cis ily', 'Cis-ily']

====================================================================================================
# M02B
====================================================================================================

## M02B FALSE POSITIVES (FP): 0 errors

*No FP errors*

## M02B FALSE NEGATIVES (FN): 80 errors

### FN #1
**Keyword:** `JB bluetooth headphones`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'JB bluetooth headphones' contains 'JB', which is a substring of 'JBL' but does not match any of the brand variations exactly. Therefore, it does not qualify as a match for the own brand.
**Context:** JBL, J-B-L, JBL-, JBL., JBLl, JBLK, JBLQ, JBLT, JBLX, JBLZ

### FN #2
**Keyword:** `jlb vibe beans`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'jlb vibe beans' contains 'vibe' and 'beans', which do not match any brand variations or related terms. However, 'jlb' is a potential typo for 'JBL', but it does not match any of the documented variations exactly. Therefore, there is no exact match for any brand terms in the keyword.
**Context:** JBL, J-B-L, JBL-, JBL., JBLl, JBLK, JBLQ, JBLT, JBLX, JBLZ

### FN #3
**Keyword:** `pioneer camp jacket`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Pioneer Camp, PioneerCamp, Pioneer-Camp, Pioneer, Pioner Camp, Pioneere Camp, Pioneer Cmap, Pionner Camp, Pioneer Cemp, Pioner Cmap

### FN #4
**Keyword:** `Pineer jacket`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'Pineer jacket' does not contain any exact match for the brand variations or related terms. The closest term 'Pioneer' is not present in the keyword.
**Context:** Pioneer Camp, PioneerCamp, Pioneer-Camp, Pioneer, Pioner Camp, Pioneere Camp, Pioneer Cmap, Pionner Camp, Pioneer Cemp, Pioner Cmap

### FN #5
**Keyword:** `Jiskaso car holder`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'Jiskaso car holder' does not contain any exact match for the brand variations or related terms. The closest term 'Jikasho' is not present in the keyword.
**Context:** Jikasho, Jikash, Jikashoo, Jikashu, Jikashp, Jikash0, Jikashow, Jikashos

### FN #6
**Keyword:** `Revlin eye liner`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'Revlin eye liner' does not contain any exact match for the brand variations 'REVLON' or 'Rev-lon', nor does it match the related term 'ColorStay'. The term 'Revlin' is not a documented variation or related term for the brand.
**Context:** REVLON, Rev-lon

### FN #7
**Keyword:** `kitchen aid oven mitt set`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'kitchen aid oven mitt set' does not contain any exact matches for 'KitchenAid' or 'Kitchen-Aid' as standalone terms. The term 'kitchen aid' is a generic descriptor and does not match the brand variations exactly.
**Context:** KitchenAid, Kitchen-Aid

### FN #8
**Keyword:** `kitchen aid oven mitt`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'kitchen aid oven mitt' does not contain any exact matches for the brand variations 'KitchenAid' or 'Kitchen-Aid'. The term 'kitchen aid' is a generic descriptor and does not match the brand name exactly.
**Context:** KitchenAid, Kitchen-Aid

### FN #9
**Keyword:** `kitchen aid gloves oven set`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword
**Context:** KitchenAid, Kitchen-Aid

### FN #10
**Keyword:** `antarctic star nugget ice maker`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Antarctic Star, AntarcticStar, Antarctic-Star, Antarctic, Antartic Star, Antarctik Star, Antrctic Star, Antarctic Staar, Antarctic Stsr, Antarctic Str

### FN #11
**Keyword:** `antarctic star countertop ice maker`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Antarctic Star, AntarcticStar, Antarctic-Star, Antarctic, Antartic Star, Antarctik Star, Antrctic Star, Antarctic Staar, Antarctic Stsr, Antarctic Str

### FN #12
**Keyword:** `antarctic star ice maker`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Antarctic Star, AntarcticStar, Antarctic-Star, Antarctic, Antartic Star, Antarctik Star, Antrctic Star, Antarctic Staar, Antarctic Stsr, Antarctic Str

### FN #13
**Keyword:** `cisiky kitchen sink caddy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Cisily, Cisly, Cicily, Cisilyy, Cisilyi, Cisilyo, Cisilyu, Cisilyt, Cisily-

### FN #14
**Keyword:** `cisily kitchen sink caddy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Cisily, Cisly, Cicily, Cisilyy, Cisilyi, Cisilyo, Cisilyu, Cisilyt, Cisily-

### FN #15
**Keyword:** `11 inch bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword '11 inch bumblebee transformer toy' contains the term 'transformer', which is a singular form of the brand 'Transformers'. However, 'Transformers' is not listed as a variation in variations_own, and the singular form does not match any documented variations. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #16
**Keyword:** `large transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #17
**Keyword:** `giant bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'giant bumblebee transformer toy'. The keyword does not contain 'Transformers', any of its variations, or 'Hasbro'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #18
**Keyword:** `transformer plush toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'transformer plush toy' contains the term 'transformer', which is a singular form of the brand 'Transformers'. However, 'Transformers' is not listed as a variation in variations_own, and the singular form is not explicitly included. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #19
**Keyword:** `perceptor transformer toy 86`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'perceptor transformer toy 86' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name listed in variations_own, and the singular form 'transformer' is not included in the variations. Therefore, it does not match any brand term exactly.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #20
**Keyword:** `green transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #21
**Keyword:** `ultra magnus transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'ultra magnus transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name in variations_own, and the singular form 'transformer' is not listed as a valid variation. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #22
**Keyword:** `alchemist prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #23
**Keyword:** `car transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #24
**Keyword:** `cyclonus transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'cyclonus transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the exact brand name in variations_own, and the singular form 'transformer' is not listed as a valid variation. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #25
**Keyword:** `pink transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'pink transformer toy' contains the term 'transformer', which is a substring of the brand 'Transformers'. However, 'transformer' is not an exact match for 'Transformers' as it is singular and the brand is plural. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #26
**Keyword:** `galvatron transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #27
**Keyword:** `soundwave transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'soundwave transformer toy'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #28
**Keyword:** `unicorn transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'unicorn transformer toy'. The term 'transformer' is singular and does not match the plural 'Transformers' in variations_own.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #29
**Keyword:** `lockdown transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #30
**Keyword:** `magnetic car transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'magnetic car transformer toy'. The term 'transformer' is singular and does not match the plural 'Transformers' in variations_own.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #31
**Keyword:** `transformer toy studio series`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'transformer toy studio series' does not contain any exact matches for the brand variations 'Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers' or the related terms 'Cyber Commander Series, Hasbro'. The term 'transformer' is singular and does not match the plural 'Transformers'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #32
**Keyword:** `monster truck transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'monster truck transformer toy'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #33
**Keyword:** `football transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'football transformer toy'. The term 'transformer' is singular and does not match the plural 'Transformers' in variations_own.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #34
**Keyword:** `cyclone hawk transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #35
**Keyword:** `wheel jack transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'wheel jack transformer toy'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #36
**Keyword:** `voice activated optimus prime`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'voice activated optimus prime' does not contain any terms from the variations_own or related_terms_own. The brand 'Transformers' is not present in the keyword, and 'optimus prime' is a character name, not a brand term.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #37
**Keyword:** `transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'transformer toy' contains 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the exact brand name in variations_own, and 'transformer' does not match it exactly. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #38
**Keyword:** `bumblebee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #39
**Keyword:** `sentinel prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'sentinel prime transformer toy' does not contain any exact matches for the brand variations or related terms. The term 'transformer' is singular and does not match the plural 'Transformers' in variations_own.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #40
**Keyword:** `bumble bee transforming toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #41
**Keyword:** `optimus prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'optimus prime transformer toy' does not contain any exact matches for the brand variations 'Transformers' or its typos, nor does it match the related terms 'Cyber Commander Series' or 'Hasbro'. The term 'transformer' is singular and does not match the plural 'Transformers'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #42
**Keyword:** `centennial prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'centennial prime transformer toy'. The keyword does not contain 'Transformers' or any of its variations.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #43
**Keyword:** `barricade transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #44
**Keyword:** `optimus prime transforming toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #45
**Keyword:** `bumble bee transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'bumble bee transformer toy' does not contain any terms from the variations_own or related_terms_own. The term 'transformer' is not an exact match for 'Transformers' (the brand name) and does not match any documented typos or related terms.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #46
**Keyword:** `shockwave transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #47
**Keyword:** `sideswipe transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #48
**Keyword:** `alpha trion transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #49
**Keyword:** `cliffjumper transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'cliffjumper transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name listed in variations_own, and the singular form 'transformer' is not included in the variations. Therefore, it does not match any brand term exactly as required.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #50
**Keyword:** `optimus prime toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #51
**Keyword:** `optimus transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'optimus transformer toy' contains the term 'transformer', which is a singular form of the brand 'Transformers'. However, 'Transformers' is not listed as a variation in variations_own, and the singular form 'transformer' is not an exact match for any of the documented variations. Therefore, it does not qualify as a match for the own brand.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #52
**Keyword:** `orion pax transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #53
**Keyword:** `bumble transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'bumble transformer toy' contains the term 'transformer', which is a substring of the brand name 'Transformers'. However, 'transformer' is not an exact match for 'Transformers' as it is singular and does not appear in the variations_own list. Therefore, it does not qualify as a match for the own brand.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #54
**Keyword:** `starscream transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'starscream transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name listed in variations_own, and the singular form 'transformer' is not included in the variations. Therefore, it does not match any brand term exactly.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #55
**Keyword:** `ratchet transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'ratchet transformer toy'. The keyword does not contain 'Transformers' or any of its variations.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #56
**Keyword:** `megatron transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'megatron transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the exact brand name in variations_own, and the singular form 'transformer' does not match any of the documented variations. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #57
**Keyword:** `transformer car toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'transformer car toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the official brand name and the keyword does not match any of the documented variations or related terms exactly. Therefore, it does not qualify as a match for the own brand.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #58
**Keyword:** `scourge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'scourge transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the exact brand name in variations_own, and the singular form 'transformer' is not listed as a valid variation. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #59
**Keyword:** `fire truck transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #60
**Keyword:** `voice activated transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'voice activated transformer toy'.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #61
**Keyword:** `metroplex transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in the keyword 'metroplex transformer toy'. The term 'transformer' is singular and does not match the plural 'Transformers' in variations_own.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #62
**Keyword:** `onyx prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'onyx prime transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name in variations_own, and the singular form 'transformer' is not listed as a valid variation. Therefore, it does not match any brand term exactly.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #63
**Keyword:** `nemesis prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'nemesis prime transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the exact brand name in variations_own, and the singular form 'transformer' does not match any of the documented variations. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #64
**Keyword:** `skurge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'skurge transformer toy' contains the term 'transformer', which is a singular form of the brand 'Transformers'. However, 'Transformers' is not listed as a variation in variations_own, and the singular form 'transformer' does not match any of the documented variations. Therefore, it does not qualify as a match for the own brand.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #65
**Keyword:** `rodimus prime transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'rodimus prime transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name in variations_own, and the singular form 'transformer' is not listed as a valid variation. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #66
**Keyword:** `apelinq transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #67
**Keyword:** `rhinox transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'rhinox transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name listed in variations_own, and the singular form 'transformer' is not included in the variations. Therefore, it does not match any documented brand term exactly.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #68
**Keyword:** `battletrap transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'battletrap transformer toy' contains the term 'transformer', which is a singular form of 'Transformers'. However, 'Transformers' is the brand name listed in variations_own, and 'transformer' is not an exact match to any of the documented variations. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #69
**Keyword:** `iron hide transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #70
**Keyword:** `toy train transformer`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #71
**Keyword:** `jetfire transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #72
**Keyword:** `helicopter transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #73
**Keyword:** `windblade transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #74
**Keyword:** `jet fire transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #75
**Keyword:** `sunstreaker transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #76
**Keyword:** `starscreen transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #77
**Keyword:** `astrotrain transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #78
**Keyword:** `cheetor transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** The keyword 'cheetor transformer toy' contains the term 'transformer', which is a substring of the brand name 'Transformers'. However, 'transformer' is not an exact match for 'Transformers' as it is singular and does not appear in the variations_own list. Therefore, it does not qualify as a match.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #79
**Keyword:** `bludgeon transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

### FN #80
**Keyword:** `scrooge transformer toy`
**Expected:** OB
**Model Output:** null
**Reasoning:** No brand terms from variations_own or related_terms_own found in keyword.
**Context:** Transformers, Transfomers, Tranfomers, Tramsformers, Transfomrers, Transformerss, Trensformers

====================================================================================================
# M04
====================================================================================================

## M04 FALSE POSITIVES (FP): 36 errors

### FP #1
**Keyword:** `oven mitt holder`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #2
**Keyword:** `kids oven mitts heat resistant`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #3
**Keyword:** `heat resistant oven mitts`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #4
**Keyword:** `high quality oven mitts`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #5
**Keyword:** `red oven mitts`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #6
**Keyword:** `ice maker with water dispenser`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #7
**Keyword:** `blue ice makers countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #8
**Keyword:** `small ice maker machine`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #9
**Keyword:** `eye concealer for mature skin`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #10
**Keyword:** `24 ounce water bottle`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Owala

### FP #11
**Keyword:** `water bottle vacuum insulated`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Owala

### FP #12
**Keyword:** `oven mitts blue`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FP #13
**Keyword:** `dorm ice maker`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #14
**Keyword:** `self cleaning ice makers countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #15
**Keyword:** `countertop pebble ice maker`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #16
**Keyword:** `nugget ice maker countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #17
**Keyword:** `red ice makers countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #18
**Keyword:** `crushed ice machine countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #19
**Keyword:** `best selling countertop ice maker`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #20
**Keyword:** `best rated countertop ice machine`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #21
**Keyword:** `portable ice maker nugget`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword contains 'nugget' which is associated with 'Nugget Ice' commonly produced by brands like Scotsman and Manitowoc, indicating a competitor brand search.
**Context:** own=Antarctic Star

### FP #22
**Keyword:** `eye liner waterproof`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #23
**Keyword:** `eye liner pencils waterproof`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #24
**Keyword:** `brown eye liner pencil`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #25
**Keyword:** `best eye liner`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #26
**Keyword:** `green eyeliner`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #27
**Keyword:** `green eye brow pencil`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #28
**Keyword:** `black jumbo eye pencil`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #29
**Keyword:** `magnetic eye liner for false lashes`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #30
**Keyword:** `brown eye brow pencil`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #31
**Keyword:** `burgundy eye liner`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #32
**Keyword:** `eye brow pencils for women`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FP #33
**Keyword:** `small ice machine`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #34
**Keyword:** `pearl ice maker`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #35
**Keyword:** `small nugget ice maker`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FP #36
**Keyword:** `ice cube maker countertop`
**Expected:** null
**Model Output:** CB
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

## M04 FALSE NEGATIVES (FN): 121 errors

### FN #1
**Keyword:** `oven mitts oxo`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oxo' which is not in the provided competitor_entities list, and does not match own brand entities.
**Context:** own=KitchenAid

### FN #2
**Keyword:** `oxo oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oxo' which is not in the competitor_entities list, and does not match own brand entities.
**Context:** own=KitchenAid

### FN #3
**Keyword:** `blue q oven mitt`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oven mitt' which is generic and does not mention any competitor brand.
**Context:** own=KitchenAid

### FN #4
**Keyword:** `sur la table oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=KitchenAid

### FN #5
**Keyword:** `oxo oven mitt`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oxo' which is not in the provided competitor_entities list, and it does not match the own brand 'KitchenAid'.
**Context:** own=KitchenAid

### FN #6
**Keyword:** `oxo silicone oven mitt`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oxo' which is not in the competitor_entities list, and does not match own brand entities.
**Context:** own=KitchenAid

### FN #7
**Keyword:** `pioneer woman oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'oven mitts' which does not match any own brand entities, and 'pioneer woman' is not in the competitor entities list.
**Context:** own=KitchenAid

### FN #8
**Keyword:** `cuisinart oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'cuisinart' which is not in the competitor_entities list, and it also does not match the own brand 'KitchenAid'.
**Context:** own=KitchenAid

### FN #9
**Keyword:** `aglucky ice makers countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'AGLUCKY' which matches own brand entity 'AGLUCKY'.
**Context:** own=Antarctic Star

### FN #10
**Keyword:** `aglucky nugget ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'AGLUCKY' which matches own brand entity 'AGLUCKY'.
**Context:** own=Antarctic Star

### FN #11
**Keyword:** `sweetcrispy countertop ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'sweetcrispy' which matches own brand 'Sweetcrispy'.
**Context:** own=Antarctic Star

### FN #12
**Keyword:** `aglucky ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'AGLUCKY' which matches own brand entity 'AGLUCKY'.
**Context:** own=Antarctic Star

### FN #13
**Keyword:** `igloo self cleaning ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'igloo' which is not in the competitor_entities list, but it is also not part of the own brand entities, so it does not indicate a competitor brand search.
**Context:** own=Antarctic Star

### FN #14
**Keyword:** `euhomy countertop ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'euhomy' which is not in the competitor_entities list, and does not match own brand entities.
**Context:** own=Antarctic Star

### FN #15
**Keyword:** `euhomy nugget ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Antarctic Star

### FN #16
**Keyword:** `euhomy ice maker machine`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which does not match any own brand entities, and does not contain any competitor brand mentions.
**Context:** own=Antarctic Star

### FN #17
**Keyword:** `aicook ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which does not match any own brand entities, and 'aicook' is not in the competitor entities list.
**Context:** own=Antarctic Star

### FN #18
**Keyword:** `igloo portable ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'igloo' which is not in the competitor_entities list, but it is also not part of the own brand entities, so it does not indicate a competitor brand search.
**Context:** own=Antarctic Star

### FN #19
**Keyword:** `amazon nugget ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which is generic and does not mention any competitor brand.
**Context:** own=Antarctic Star

### FN #20
**Keyword:** `euhomy ice machine`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice machine' which does not match any own brand entities, and does not reference any competitor brands.
**Context:** own=Antarctic Star

### FN #21
**Keyword:** `simzlife ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which does not match any competitor entity, and 'simzlife' is not in the own brand list.
**Context:** own=Antarctic Star

### FN #22
**Keyword:** `orgo ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which does not match any own brand entities, and it does not contain any competitor brand mentions.
**Context:** own=Antarctic Star

### FN #23
**Keyword:** `euhomy ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ice maker' which does not match any competitor brand, and 'euhomy' is not in the competitor_entities list.
**Context:** own=Antarctic Star

### FN #24
**Keyword:** `color pop eye shadow`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FN #25
**Keyword:** `wonderskin eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'wonderskin' which exactly matches own brand entity 'Wonderskin'.
**Context:** own=REVLON

### FN #26
**Keyword:** `1440 wonderskin eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'wonderskin' which matches own brand 'Wonderskin'.
**Context:** own=REVLON

### FN #27
**Keyword:** `nix eye liners`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FN #28
**Keyword:** `color stay eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'color stay' which matches own brand entity 'Color Stay'.
**Context:** own=REVLON

### FN #29
**Keyword:** `thrive infinity waterproof eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'thrive' which is not in own brand entities, and does not match any competitor brand.
**Context:** own=REVLON

### FN #30
**Keyword:** `occasionalous 24 hr waterproof eyeliner duo sharpenable eye pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=REVLON

### FN #31
**Keyword:** `ayky long wear gel eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eyeliner' which is a generic term and does not reference any competitor brand.
**Context:** own=REVLON

### FN #32
**Keyword:** `eye embrace eyebrow pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eyebrow pencil' which is generic and does not mention any competitor brand.
**Context:** own=REVLON

### FN #33
**Keyword:** `prime eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, so we proceed to check for competitors.
**Context:** own=REVLON

### FN #34
**Keyword:** `primeprometics eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'primeprometics' which matches own brand entity 'Revlon'.
**Context:** own=REVLON

### FN #35
**Keyword:** `persona eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eye liner' which does not match any own brand entities, and does not mention any competitor brands.
**Context:** own=REVLON

### FN #36
**Keyword:** `nyc jumbo eye pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, so we proceed to check for competitors.
**Context:** own=REVLON

### FN #37
**Keyword:** `jmcy eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eye liner' which does not match any own brand entities, and does not mention any competitor brands.
**Context:** own=REVLON

### FN #38
**Keyword:** `kissme eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eye liner' which does not match any own brand entities, and does not mention any competitor brand.
**Context:** own=REVLON

### FN #39
**Keyword:** `infallible eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'eyeliner' which is a generic term and does not mention any competitor brand.
**Context:** own=REVLON

### FN #40
**Keyword:** `1440 longwear eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, so we proceed to check for competitors.
**Context:** own=REVLON

### FN #41
**Keyword:** `primeeyes glide eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'glide eyeliner' which does not match any own brand entities, and 'primeeyes' is not in the competitor list.
**Context:** own=REVLON

### FN #42
**Keyword:** `maifan sink caddy`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Cisily

### FN #43
**Keyword:** `hapiRM sink caddy organizer`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Cisily

### FN #44
**Keyword:** `Yieach caddy sink organizer`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Cisily

### FN #45
**Keyword:** `spyder packable puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Pioneer Camp

### FN #46
**Keyword:** `flip straw tumbler 30 oz`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Owala

### FN #47
**Keyword:** `flip straw tumbler 20 oz`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #48
**Keyword:** `cortland`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword 'cortland' does not match any own brand entities and does not reference any competitor brand.
**Context:** own=Owala

### FN #49
**Keyword:** `iton flask`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'flask' which is a common term and does not match any competitor brand in the provided list.
**Context:** own=Owala

### FN #50
**Keyword:** `tal water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Owala

### FN #51
**Keyword:** `autoseal water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'water bottle' which is generic and does not mention any competitor brand.
**Context:** own=Owala

### FN #52
**Keyword:** `owala water bottle boot`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #53
**Keyword:** `owala water bottle lid parts`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #54
**Keyword:** `owala water bottle top`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #55
**Keyword:** `owala water bottle 32oz boot`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #56
**Keyword:** `owala water bottle lid`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #57
**Keyword:** `owala water bottle accessories`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #58
**Keyword:** `owala water bottle insulated`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #59
**Keyword:** `owala water bottle with straw`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #60
**Keyword:** `owala water bottle leak proof`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #61
**Keyword:** `owala flip water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #62
**Keyword:** `freesip owala water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #63
**Keyword:** `owala freesip sway insulated stainless steel water bottle with two-way spout`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owala' which matches own brand entity 'Owala'.
**Context:** own=Owala

### FN #64
**Keyword:** `Owalaa SS water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Owalaa' which matches own brand entity 'Owalaa'.
**Context:** own=Owala

### FN #65
**Keyword:** `heart earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword 'heart earbuds' does not match any own brand entities, and it does not contain any competitor brand mentions.
**Context:** own=JBL

### FN #66
**Keyword:** `alexa earbuds wireless 2024`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'alexa' which is not in competitor_entities list, and 'earbuds' is generic, indicating no specific brand mention.
**Context:** own=JBL

### FN #67
**Keyword:** `tozo wireless earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'tozo' which matches own brand entity 'TOZO'.
**Context:** own=JBL

### FN #68
**Keyword:** `jlab earbuds wireless`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'jlab' which matches own brand entity 'JLab'.
**Context:** own=JBL

### FN #69
**Keyword:** `amazon ear buds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ear buds' which does not match any own brand entities, and does not mention any competitor brands.
**Context:** own=JBL

### FN #70
**Keyword:** `alexa earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'alexa' which is not in the competitor_entities list, and 'earbuds' is a generic term without brand mention.
**Context:** own=JBL

### FN #71
**Keyword:** `amazon noise cancelling earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'earbuds' which is generic and does not mention any competitor brand.
**Context:** own=JBL

### FN #72
**Keyword:** `beats solo buds`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'buds' which is a common term and does not specifically reference a competitor brand.
**Context:** own=JBL

### FN #73
**Keyword:** `echo ear buds 2025 edition`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ear buds' which does not match any own brand entities, and does not reference any competitor brands.
**Context:** own=JBL

### FN #74
**Keyword:** `amazon ear bud`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ear bud' which is generic and does not reference any competitor brand.
**Context:** own=JBL

### FN #75
**Keyword:** `amazon basics jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'amazon' which is not in competitor_entities list, indicating it is likely the seller's own brand.
**Context:** own=Pioneer Camp

### FN #76
**Keyword:** `gerry down jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'down jacket' which is a generic term and does not reference any competitor brand.
**Context:** own=Pioneer Camp

### FN #77
**Keyword:** `spider jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Pioneer Camp

### FN #78
**Keyword:** `magcomsen jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'magcomsen' which does not match any own brand entities, allowing for competitor analysis.
**Context:** own=Pioneer Camp

### FN #79
**Keyword:** `amazon puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'puffer jacket' which is generic and does not mention any competitor brand.
**Context:** own=Pioneer Camp

### FN #80
**Keyword:** `amazon jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword 'amazon jacket' does not contain any own brand entities, and it is a generic term without any competitor brand mention.
**Context:** own=Pioneer Camp

### FN #81
**Keyword:** `amazon jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'jacket' which is a generic term and does not reference any competitor brand.
**Context:** own=Pioneer Camp

### FN #82
**Keyword:** `spider jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword 'spider jacket' does not match any own brand entities, and it does not contain any competitor brand mentions.
**Context:** own=Pioneer Camp

### FN #83
**Keyword:** `ariat puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'ariat' which is not in the competitor_entities list, and it does not match any own brand entities.
**Context:** own=Pioneer Camp

### FN #84
**Keyword:** `woobie jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword 'woobie jacket' does not match any own brand entities, allowing for competitor analysis.
**Context:** own=Pioneer Camp

### FN #85
**Keyword:** `gerry jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Pioneer Camp

### FN #86
**Keyword:** `gerry puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'gerry' which does not match any own brand entities, and 'puffer jacket' is a generic term without competitor brand mention.
**Context:** own=Pioneer Camp

### FN #87
**Keyword:** `nixivie magnet phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'nixivie' which is not in the competitor_entities list, and does not match own brand entities.
**Context:** own=Jikasho

### FN #88
**Keyword:** `nixiveofficial magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'nixiveofficial' which is not in the competitor_entities list, and it also contains 'Jikasho' which is in own_brand.entities.
**Context:** own=Jikasho

### FN #89
**Keyword:** `gripmaster pro 360 magnetic holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'gripmaster' which does not match any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #90
**Keyword:** `vipbugo vacuum magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'vipbugo' which matches own brand entity 'Jikasho'.
**Context:** own=Jikasho

### FN #91
**Keyword:** `msxttly vacuum magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'msxttly' which does not match any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #92
**Keyword:** `veltrix phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #93
**Keyword:** `tenikle phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #94
**Keyword:** `noxive phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'noxive' which is not in the own brand entities list, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #95
**Keyword:** `vipbugo phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'vipbugo' which matches own brand entity 'Jikasho'.
**Context:** own=Jikasho

### FN #96
**Keyword:** `autobriva phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #97
**Keyword:** `magic john phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'john' which does not match any own brand entities, and 'magic' is not a competitor brand either.
**Context:** own=Jikasho

### FN #98
**Keyword:** `voowow phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'voowow' which is not in the competitor_entities list, and it does not match any own brand entities.
**Context:** own=Jikasho

### FN #99
**Keyword:** `eagerlyus phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'phone holder' which does not match any competitor brand, and there are no competitor entities present.
**Context:** own=Jikasho

### FN #100
**Keyword:** `kaston phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'kaston' which does not match any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #101
**Keyword:** `mrglas phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Jikasho

### FN #102
**Keyword:** `nixiveofficial phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'nixiveofficial' which is not in the competitor_entities list, and it also contains 'phone holder' which is generic and does not reference any specific brand.
**Context:** own=Jikasho

### FN #103
**Keyword:** `nixie phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, allowing for competitor analysis.
**Context:** own=Jikasho

### FN #104
**Keyword:** `Batman figure`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Transformers

### FN #105
**Keyword:** `one care pen needles 32g 4mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=Rx Crush

### FN #106
**Keyword:** `one care pen needles`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=Rx Crush

### FN #107
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #108
**Keyword:** `easy touch syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #109
**Keyword:** `syringes easytouch`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #110
**Keyword:** `syring basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #111
**Keyword:** `syringes med line`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #112
**Keyword:** `one care pen needles 32g 4mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=Rx Crush

### FN #113
**Keyword:** `Colorstay liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'Colorstay' which matches own brand entity 'ColorStay'.
**Context:** own=REVLON

### FN #114
**Keyword:** `one care pen needles`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any terms from own brand entities, allowing for competitor analysis.
**Context:** own=Rx Crush

### FN #115
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #116
**Keyword:** `easy touch syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #117
**Keyword:** `syringes easytouch`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #118
**Keyword:** `syring basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #119
**Keyword:** `syringes med line`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #120
**Keyword:** `easy touch syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword does not contain any own brand entities, proceeding to competitor check.
**Context:** own=Rx Crush

### FN #121
**Keyword:** `bh supplies`
**Expected:** CB
**Model Output:** null
**Reasoning:** Keyword contains 'bh supplies' which matches own brand 'BH Supplies'.
**Context:** own=Rx Crush

====================================================================================================
# M04B
====================================================================================================

## M04B FALSE POSITIVES (FP): 5 errors

### FP #1
**Keyword:** `lego toy`
**Expected:** null
**Model Output:** CB
**Reasoning:** The keyword 'lego toy' contains 'lego', which is a well-known brand name for construction toys. This matches the criteria for a competitor brand classification.
**Context:** own=Transformers

### FP #2
**Keyword:** `11 inch bumblebee transformer toy`
**Expected:** null
**Model Output:** CB
**Reasoning:** The keyword '11 inch bumblebee transformer toy' contains the term 'transformer', which is a direct reference to the 'Transformers' brand. This brand is associated with the toy line produced by Hasbro, making it a competitor brand in this context.
**Context:** own=Transformers

### FP #3
**Keyword:** `wheel jack transformer toy`
**Expected:** null
**Model Output:** CB
**Reasoning:** The keyword 'wheel jack transformer toy' contains the term 'transformer', which is a direct reference to the brand 'Transformers'. This brand is recognized as a competitor in the toy category, specifically related to action figures and toys based on the Transformers franchise.
**Context:** own=Transformers

### FP #4
**Keyword:** `optimus prime transforming toy`
**Expected:** null
**Model Output:** CB
**Reasoning:** The keyword 'optimus prime transforming toy' contains 'Optimus Prime', which is a character from the Transformers franchise owned by Hasbro. This character is widely recognized and functions as a brand identifier in the toy category, thus qualifying as a competitor brand reference.
**Context:** own=Transformers

### FP #5
**Keyword:** `optimus prime toy`
**Expected:** null
**Model Output:** CB
**Reasoning:** The keyword 'optimus prime toy' contains 'Optimus Prime', which is a character from the Transformers franchise owned by Hasbro. Although 'Transformers' is the own brand, 'Optimus Prime' is a well-known character that functions as a brand identifier in the toy category, thus qualifying as a competitor brand reference.
**Context:** own=Transformers

## M04B FALSE NEGATIVES (FN): 210 errors

### FN #1
**Keyword:** `homwe silicone oven mitt`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'homwe silicone oven mitt' does not contain any competitor brand terms from the provided list. 'Homwe' is recognized as a brand in the kitchen category, but it is not listed among the competitors. Therefore, it does not qualify as a competitor brand match.
**Context:** own=KitchenAid

### FN #2
**Keyword:** `gorilla grip oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'gorilla grip oven mitts' does not contain any competitor brand terms. 'Gorilla Grip' is a brand name, but it is not listed among the competitors provided. The other words in the keyword are generic descriptors and do not refer to any known brands.
**Context:** own=KitchenAid

### FN #3
**Keyword:** `martha stewart oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'martha stewart oven mitts' does not contain any competitor brand terms. It is a generic description of oven mitts associated with the Martha Stewart brand, which is not listed as a competitor in the provided data. Therefore, it does not match any competitor brand from the list.
**Context:** own=KitchenAid

### FN #4
**Keyword:** `all clad oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'all clad oven mitts' does not contain any competitor brand terms. 'All Clad' is a brand name, but it is not listed as a competitor in the provided data. The term 'all clad' is also a common phrase and does not match any competitor brand variations or related terms. Therefore, it is classified as null.
**Context:** own=KitchenAid

### FN #5
**Keyword:** `blue q oven mitt`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'blue q oven mitt' does not contain any competitor brand terms from the provided list. It is purely descriptive and does not reference any known brands or variations.
**Context:** own=KitchenAid

### FN #6
**Keyword:** `sur la table oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'sur la table oven mitts' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=KitchenAid

### FN #7
**Keyword:** `pioneer woman oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'pioneer woman oven mitts' does not contain any competitor brand terms from the provided list. 'Pioneer Woman' is a recognized brand but is not listed as a competitor in the provided data. All other words in the keyword are generic descriptors related to the product type.
**Context:** own=KitchenAid

### FN #8
**Keyword:** `william sonoma oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'william sonoma oven mitts' does not contain any competitor brand terms from the provided list. 'William Sonoma' is a recognized brand but is not listed as a competitor in the provided data. The other words in the keyword are generic descriptors related to the product type.
**Context:** own=KitchenAid

### FN #9
**Keyword:** `cuisinart oven mitts`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cuisinart oven mitts' does not contain any competitor brand terms. 'Cuisinart' is the own brand and is not listed among the competitors. The other words are generic descriptors related to the product type.
**Context:** own=KitchenAid

### FN #10
**Keyword:** `ipod headphones`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ipod headphones' does not contain any competitor brand terms from the provided list. It is a generic term referring to headphones compatible with iPods, which is a product category rather than a specific brand name. No recognizable brands or variations were found in the keyword.
**Context:** own=JBL

### FN #11
**Keyword:** `beats over ear headphones`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'beats over ear headphones' does not contain any competitor brand terms from the provided list. 'Beats' is a brand, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=JBL

### FN #12
**Keyword:** `heart earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'heart earbuds' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to audio products without any identifiable brand names or variations.
**Context:** own=JBL

### FN #13
**Keyword:** `raycon bluetooth earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'raycon bluetooth earbuds' does not contain any competitor brand terms from the provided list. 'Raycon' is a brand itself, but it is not listed as a competitor. The other terms are generic descriptors for the product type and do not correspond to any known competitor brands.
**Context:** own=JBL

### FN #14
**Keyword:** `raycon earbuds wireless`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'raycon earbuds wireless' does not contain any competitor brand terms from the provided list. 'Raycon' is a brand itself, but it is not listed as a competitor. The terms 'earbuds' and 'wireless' are generic descriptors and do not refer to any specific brand.
**Context:** own=JBL

### FN #15
**Keyword:** `alexa earbuds wireless 2024`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'alexa earbuds wireless 2024' does not contain any competitor brand terms. It is a generic description of a product and does not reference any specific brand from the provided competitor list.
**Context:** own=JBL

### FN #16
**Keyword:** `tozo wireless earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'tozo wireless earbuds' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any recognizable brand names or variations present.
**Context:** own=JBL

### FN #17
**Keyword:** `jlab earbuds wireless`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'jlab earbuds wireless' does not contain any competitor brand terms. It does not match any of the competitor brands listed (Apple, Sony, Bose, Soundcore) or their variations. The term 'jlab' is not recognized as a competitor brand and does not correspond to any known brands in the audio category.
**Context:** own=JBL

### FN #18
**Keyword:** `raycon fitness earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'raycon fitness earbuds' does not contain any competitor brand terms from the provided list. 'Raycon' is a brand name, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=JBL

### FN #19
**Keyword:** `raycon earbud`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'raycon earbud' does not contain any competitor brand terms from the provided list. 'Raycon' is not recognized as a competitor brand in this context, and there are no other recognizable brands present in the keyword.
**Context:** own=JBL

### FN #20
**Keyword:** `echobuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'echobuds' contains 'Echo', which is a product line from Amazon, but it does not match any of the competitor brands listed. Therefore, it does not qualify as a competitor brand term.
**Context:** own=JBL

### FN #21
**Keyword:** `amazon ear buds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon ear buds' contains no competitor brand terms. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=JBL

### FN #22
**Keyword:** `alexa earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'alexa earbuds' does not contain any competitor brand terms from the provided list. 'Alexa' is associated with Amazon's own brand and 'earbuds' is a generic term for a type of audio device. Therefore, it does not qualify as a competitor brand.
**Context:** own=JBL

### FN #23
**Keyword:** `earpods iphone`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'earpods iphone' does not contain any competitor brand terms. It is a generic term referring to earphones compatible with iPhones. No recognizable brands or variations from the competitor list are present.
**Context:** own=JBL

### FN #24
**Keyword:** `bluetooth earbuds tozo`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'bluetooth earbuds tozo' does not contain any competitor brand terms from the provided list. 'Tozo' is not recognized as a competitor brand, and there are no other identifiable brands present in the keyword.
**Context:** own=JBL

### FN #25
**Keyword:** `amazon noise cancelling earbuds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon noise cancelling earbuds' contains no competitor brand terms, variations, or related terms. It is purely descriptive and does not reference any known brands in the audio category.
**Context:** own=JBL

### FN #26
**Keyword:** `beats solo buds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'beats solo buds' does not contain any competitor brand terms from the provided list. 'Beats' is a brand, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=JBL

### FN #27
**Keyword:** `ear buds galaxy`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ear buds galaxy' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific brand or variation.
**Context:** own=JBL

### FN #28
**Keyword:** `beats buds`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'beats buds' does not contain any competitor brand terms from the provided list. 'Beats' is a brand, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=JBL

### FN #29
**Keyword:** `echo ear buds 2025 edition`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'echo ear buds 2025 edition' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known brands or variations.
**Context:** own=JBL

### FN #30
**Keyword:** `silver beats`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'silver beats' does not contain any competitor brand terms from the provided list. 'Beats' could refer to the brand 'Beats by Dre', but it is not included in the competitor list. Therefore, it is classified as a non-branded keyword.
**Context:** own=JBL

### FN #31
**Keyword:** `beats earbuds with microphone`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'beats earbuds with microphone' does not contain any competitor brand terms from the provided list. 'Beats' is a brand, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=JBL

### FN #32
**Keyword:** `amazon ear bud`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon ear bud' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific brand or variation.
**Context:** own=JBL

### FN #33
**Keyword:** `maifan sink caddy`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'maifan sink caddy' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to a sink caddy and does not reference any known brands or variations.
**Context:** own=Cisily

### FN #34
**Keyword:** `hapiRM sink caddy organizer`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'hapiRM sink caddy organizer' does not contain any competitor brand terms from the provided list. All words are generic descriptors related to the product type and do not reference any known brands.
**Context:** own=Cisily

### FN #35
**Keyword:** `Ox Sink Caddy`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'Ox Sink Caddy' does not contain any competitor brand terms. The term 'Ox' is not a recognized brand and does not match any variations or related terms from the competitor list. Additionally, 'Sink Caddy' is a generic product descriptor.
**Context:** own=Cisily

### FN #36
**Keyword:** `Yieach caddy sink organizer`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'Yieach caddy sink organizer' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations.
**Context:** own=Cisily

### FN #37
**Keyword:** `spyder rain jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder rain jacket men' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in outdoor apparel, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #38
**Keyword:** `spyder rain jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder rain jacket' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in outdoor apparel, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #39
**Keyword:** `spyder packable puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder packable puffer jacket' does not contain any competitor brand terms from the provided list. The term 'spyder' does not match any known competitor brands or their variations. It is also not a recognized brand in the outdoor apparel category. Therefore, it is classified as null.
**Context:** own=Pioneer Camp

### FN #40
**Keyword:** `amazon basics jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon basics jacket' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known brands or variations.
**Context:** own=Pioneer Camp

### FN #41
**Keyword:** `spyder puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder puffer jacket' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in the outdoor apparel category, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #42
**Keyword:** `gerry down jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'gerry down jacket' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Pioneer Camp

### FN #43
**Keyword:** `spider jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spider jacket men' contains no competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Pioneer Camp

### FN #44
**Keyword:** `Colorstay liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'Colorstay liner' contains 'ColorStay', which is a related term for the own brand REVLON. Therefore, it does not qualify as a competitor brand keyword.
**Context:** own=REVLON

### FN #45
**Keyword:** `cambro tray`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cambro tray' does not contain any competitor brand terms from the provided list. 'Cambro' is not recognized as a competitor brand in the kitchen product category, and there are no variations or related terms that match. All words in the keyword are generic descriptors.
**Context:** own=WEBACOO

### FN #46
**Keyword:** `ironflask 40 oz`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ironflask 40 oz' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any known brands or variations.
**Context:** own=Owala

### FN #47
**Keyword:** `camel back`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camel back' does not contain any competitor brand terms from the provided list. It is a generic phrase and does not reference any known brands or variations.
**Context:** own=Owala

### FN #48
**Keyword:** `iceflow flip straw tumbler`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'iceflow flip straw tumbler' does not contain any competitor brand terms. It does not match any variations or related terms from the competitor brands listed, nor does it reference any known brands in the category. All terms are generic descriptors related to the product type.
**Context:** own=Owala

### FN #49
**Keyword:** `chute`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'chute' does not contain any competitor brand terms, variations, or related terms. It is a generic word and does not refer to any specific brand or product line.
**Context:** own=Owala

### FN #50
**Keyword:** `ice flow`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ice flow' does not contain any competitor brand terms from the provided list. It is a generic phrase and does not reference any specific brand or product line.
**Context:** own=Owala

### FN #51
**Keyword:** `camel bak waterbottles`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camel bak waterbottles' does not contain any competitor brand terms from the provided list. 'CamelBak' is a recognized brand, but it is not included in the competitor list. The term 'waterbottles' is generic and does not refer to any specific brand.
**Context:** own=Owala

### FN #52
**Keyword:** `flip straw tumbler 30 oz`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'flip straw tumbler 30 oz' contains no competitor brand terms, variations, or related terms. All words are generic descriptors related to the product type and do not reference any known brands.
**Context:** own=Owala

### FN #53
**Keyword:** `canelbak`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'canelbak' does not match any competitor brand terms or variations. It appears to be a misspelling or variation of 'CamelBak', which is not included in the provided competitor list. Therefore, it does not qualify as a competitor brand reference.
**Context:** own=Owala

### FN #54
**Keyword:** `camelback bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camelback bottle' does not contain any competitor brand terms from the provided list. It is a generic description of a type of bottle and does not reference any specific brand or variation.
**Context:** own=Owala

### FN #55
**Keyword:** `flip straw tumbler 20 oz`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'flip straw tumbler 20 oz' contains no competitor brand terms, variations, or related terms. All words are generic descriptors related to the product type and do not reference any known brands.
**Context:** own=Owala

### FN #56
**Keyword:** `camel bak bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camel bak bottle' does not contain any competitor brand terms from the provided list. 'CamelBak' is a recognized brand, but it is not included in the competitor list. The keyword does not match any known brands or variations, nor does it contain any generic descriptors that would indicate a brand presence.
**Context:** own=Owala

### FN #57
**Keyword:** `cortland`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cortland' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor is it a known brand in the kitchen products category.
**Context:** own=Owala

### FN #58
**Keyword:** `camel back water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camel back water bottle' does not contain any competitor brand terms from the provided list. It is a generic description of a type of water bottle and does not reference any specific brand or variation.
**Context:** own=Owala

### FN #59
**Keyword:** `camel back waterbottles`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'camel back waterbottles' does not contain any competitor brand terms from the provided list. It is a generic description of a type of water bottle and does not reference any specific brand or variation.
**Context:** own=Owala

### FN #60
**Keyword:** `camelback`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'camelback' does not match any competitor brand terms or variations. It is a standalone term and does not contain any recognizable competitor brand names from the provided list.
**Context:** own=Owala

### FN #61
**Keyword:** `iton flask`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'iton flask' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it represent a known brand in the category. The term 'iton' does not correspond to any recognized brand, and 'flask' is a generic term for a type of container.
**Context:** own=Owala

### FN #62
**Keyword:** `iceflow`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'iceflow' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it represent a known brand in the category. Therefore, it is classified as a non-branded keyword.
**Context:** own=Owala

### FN #63
**Keyword:** `tal water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'tal water bottle' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Owala

### FN #64
**Keyword:** `autoseal water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'autoseal water bottle' does not contain any competitor brand terms from the provided list. It is a generic description of a type of water bottle and does not reference any specific brand or variation.
**Context:** own=Owala

### FN #65
**Keyword:** `coldest water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'coldest water bottle' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=Owala

### FN #66
**Keyword:** `owala water bottle boot`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle boot' contains the own brand term 'Owala', which is part of the own brand verification. Therefore, it cannot be classified as a competitor brand.
**Context:** own=Owala

### FN #67
**Keyword:** `owala water bottle lid parts`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle lid parts' contains the own brand term 'Owala', which is explicitly listed in the own brand verification. Therefore, it cannot be classified as a competitor brand.
**Context:** own=Owala

### FN #68
**Keyword:** `owala water bottle top`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle top' contains the own brand term 'Owala', which is explicitly listed in the own brand variations. Therefore, it cannot be classified as a competitor brand.
**Context:** own=Owala

### FN #69
**Keyword:** `owala water bottle 32oz boot`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle 32oz boot' contains the own brand term 'Owala', which is the brand name of the product. Therefore, it does not contain any competitor brand terms and should be classified as null.
**Context:** own=Owala

### FN #70
**Keyword:** `owala water bottle lid`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle lid' contains the own brand term 'Owala', which is explicitly listed in the own brand verification. Therefore, it cannot be classified as a competitor brand.
**Context:** own=Owala

### FN #71
**Keyword:** `owala water bottle accessories`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'owala water bottle accessories' contains the own brand 'Owala' and does not reference any competitor brands. The term 'owala' is part of the own brand's name and is not a competitor brand.
**Context:** own=Owala

### FN #72
**Keyword:** `owala water bottle insulated`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle insulated' contains the own brand term 'Owala', which is the brand name of the product. Therefore, it does not qualify as a competitor brand keyword.
**Context:** own=Owala

### FN #73
**Keyword:** `owala water bottle with straw`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle with straw' contains the own brand term 'Owala', which is the brand name of the product. Therefore, it does not contain a competitor brand term and should be classified as null.
**Context:** own=Owala

### FN #74
**Keyword:** `owala water bottle leak proof`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala water bottle leak proof' contains the own brand term 'Owala', which is the brand name of the product. Therefore, it does not contain any competitor brand terms and should be classified as null.
**Context:** own=Owala

### FN #75
**Keyword:** `owala flip water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'owala flip water bottle' contains the own brand term 'Owala', which is the brand name of the product. Therefore, it does not contain any competitor brand terms and should be classified as null.
**Context:** own=Owala

### FN #76
**Keyword:** `freesip owala water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'freesip owala water bottle' contains the own brand term 'Owala', which is part of the own brand verification. Therefore, it cannot be classified as a competitor brand.
**Context:** own=Owala

### FN #77
**Keyword:** `owala freesip sway insulated stainless steel water bottle with two-way spout`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'owala freesip sway insulated stainless steel water bottle with two-way spout' does not contain any competitor brand terms. It is primarily descriptive of the product features and does not reference any known competitor brands or their variations.
**Context:** own=Owala

### FN #78
**Keyword:** `Owalaa SS water bottle`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'Owalaa SS water bottle' contains 'Owalaa', which is a variation of the own brand 'Owala'. Therefore, it does not contain a competitor brand term and should be classified as null.
**Context:** own=Owala

### FN #79
**Keyword:** `aglucky ice makers countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'aglucky ice makers countertop' does not contain any competitor brand terms from the provided list. It is purely descriptive and does not reference any known brands or variations.
**Context:** own=Antarctic Star

### FN #80
**Keyword:** `aglucky nugget ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'aglucky nugget ice maker countertop' does not contain any competitor brand terms from the provided list. It consists of generic descriptors and does not reference any known brands or variations.
**Context:** own=Antarctic Star

### FN #81
**Keyword:** `zafro ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'zafro ice maker countertop' does not contain any competitor brand terms from the provided list. It is purely descriptive and does not reference any known brands or variations.
**Context:** own=Antarctic Star

### FN #82
**Keyword:** `sweetcrispy countertop ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'sweetcrispy countertop ice maker' contains no competitor brand terms. It is purely descriptive and does not reference any known brands or variations from the competitor list.
**Context:** own=Antarctic Star

### FN #83
**Keyword:** `aglucky ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'aglucky ice maker' does not contain any competitor brand terms from the provided list. It appears to be a generic product description without any recognizable brand names or variations.
**Context:** own=Antarctic Star

### FN #84
**Keyword:** `igloo ice`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo ice' does not contain any competitor brand terms from the provided list. It consists of generic words related to ice and does not reference any known brands or variations.
**Context:** own=Antarctic Star

### FN #85
**Keyword:** `igloo portable ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo portable ice maker countertop' contains no competitor brand terms. All words are generic descriptors related to the product type and do not reference any known brands from the provided competitor list.
**Context:** own=Antarctic Star

### FN #86
**Keyword:** `igloo self cleaning ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo self cleaning ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Antarctic Star

### FN #87
**Keyword:** `igloo ice makers countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo ice makers countertop' contains no competitor brand terms. All words are generic descriptors related to ice makers and do not reference any known brands from the provided competitor list.
**Context:** own=Antarctic Star

### FN #88
**Keyword:** `igloo nugget ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo nugget ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any recognizable brand names or variations present.
**Context:** own=Antarctic Star

### FN #89
**Keyword:** `igloo countertop ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo countertop ice maker' does not contain any competitor brand terms from the provided list. It is purely descriptive of the product type and does not reference any known brands or variations.
**Context:** own=Antarctic Star

### FN #90
**Keyword:** `igloo ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo ice maker countertop' contains no competitor brand terms. All words are generic descriptors related to the product type and do not reference any known brands from the provided competitor list.
**Context:** own=Antarctic Star

### FN #91
**Keyword:** `euhomy countertop ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'euhomy countertop ice maker' does not contain any competitor brand terms. The term 'euhomy' is the own brand and is not a competitor. All other words are generic descriptors related to the product type.
**Context:** own=Antarctic Star

### FN #92
**Keyword:** `countertop ice maker igloo`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'countertop ice maker igloo' does not contain any competitor brand terms from the provided list. The terms 'countertop', 'ice maker', and 'igloo' are generic descriptors and do not correspond to any known brands or variations.
**Context:** own=Antarctic Star

### FN #93
**Keyword:** `euhomy nugget ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'euhomy nugget ice maker countertop' contains the term 'Euhomy', which is a variation of the own brand 'EUHOMY'. Therefore, it does not qualify as a competitor brand keyword.
**Context:** own=Antarctic Star

### FN #94
**Keyword:** `pink igloo ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'pink igloo ice maker' does not contain any competitor brand terms from the provided list. All words are generic descriptors related to the product type and do not reference any specific brand.
**Context:** own=Antarctic Star

### FN #95
**Keyword:** `insignia ice makers countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'insignia ice makers countertop' does not contain any competitor brand terms from the provided list. The term 'insignia' does not match any known competitor brands, variations, or related terms. Additionally, all other words in the keyword are generic descriptors related to the product type.
**Context:** own=Antarctic Star

### FN #96
**Keyword:** `euhomy ice maker machine`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'euhomy ice maker machine' does not contain any competitor brand terms. It is a generic description of a product type and does not reference any known brands from the provided competitor list or any recognizable brands in the category.
**Context:** own=Antarctic Star

### FN #97
**Keyword:** `aicook ice maker countertop`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'aicook ice maker countertop' does not contain any competitor brand terms. It is a generic description of a product and does not reference any known brands from the provided competitor list.
**Context:** own=Antarctic Star

### FN #98
**Keyword:** `igloo portable ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo portable ice maker' contains no competitor brand terms. It is a generic description of a product type and does not reference any known brands from the provided competitor list.
**Context:** own=Antarctic Star

### FN #99
**Keyword:** `amazon nugget ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon nugget ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Antarctic Star

### FN #100
**Keyword:** `igloo ice machine`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo ice machine' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any recognizable brand names or variations present.
**Context:** own=Antarctic Star

### FN #101
**Keyword:** `simzlife ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'simzlife ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Antarctic Star

### FN #102
**Keyword:** `ge ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ge ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=Antarctic Star

### FN #103
**Keyword:** `igloo ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'igloo ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific brand or recognizable competitor.
**Context:** own=Antarctic Star

### FN #104
**Keyword:** `orgo ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'orgo ice maker' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=Antarctic Star

### FN #105
**Keyword:** `euhomy ice maker`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'euhomy ice maker' does not contain any competitor brand terms. It is a generic description of a product type. The own brand 'Antarctic Star' is also not present in the keyword, confirming that it does not refer to any competitor brand.
**Context:** own=Antarctic Star

### FN #106
**Keyword:** `spyder jacket women`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder jacket women' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in the outdoor apparel category, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #107
**Keyword:** `magcomsen jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'magcomsen jacket' does not contain any competitor brand terms from the provided list. It appears to be a generic product description without any recognizable brand names or variations.
**Context:** own=Pioneer Camp

### FN #108
**Keyword:** `spyder fleece jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder fleece jacket men' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in the outdoor apparel category, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #109
**Keyword:** `amazon puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon puffer jacket' contains no competitor brand terms. It is a generic description of a product without any identifiable brand names or variations present.
**Context:** own=Pioneer Camp

### FN #110
**Keyword:** `amazon jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon jacket' contains no competitor brand terms, variations, or related terms. It is purely descriptive and does not reference any known brands in the provided competitor list or common brands in the category.
**Context:** own=Pioneer Camp

### FN #111
**Keyword:** `spyder jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder jacket' does not contain any competitor brand terms from the provided list. 'Spyder' is a recognized brand in the outdoor apparel category, but it is not listed among the competitors provided. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Pioneer Camp

### FN #112
**Keyword:** `amazon jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon jacket men' contains no competitor brand terms, variations, or related terms. All words are generic descriptors related to jackets and do not reference any specific brand.
**Context:** own=Pioneer Camp

### FN #113
**Keyword:** `spyder jacket men`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spyder jacket men' does not contain any competitor brand terms from the provided list. 'Spyder' is not recognized as a competitor brand in this context, and there are no other recognizable brands present in the keyword.
**Context:** own=Pioneer Camp

### FN #114
**Keyword:** `spider jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'spider jacket' does not contain any competitor brand terms from the provided list. It is a generic description and does not reference any known brands or variations.
**Context:** own=Pioneer Camp

### FN #115
**Keyword:** `amazon essential puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'amazon essential puffer jacket' contains no competitor brand terms. It is a generic description of a product and does not reference any known brands from the provided competitor list or any recognizable brands in the category.
**Context:** own=Pioneer Camp

### FN #116
**Keyword:** `ariat puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ariat puffer jacket' does not contain any competitor brand terms from the provided list. 'Ariat' is not recognized as a competitor brand in the context of the given competitors, and there are no other recognizable brands present in the keyword.
**Context:** own=Pioneer Camp

### FN #117
**Keyword:** `woobie jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'woobie jacket' does not contain any competitor brand terms from the provided list. It is a generic term and does not reference any known brands or variations.
**Context:** own=Pioneer Camp

### FN #118
**Keyword:** `gerry jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'gerry jacket' does not contain any competitor brand terms from the provided list. It is a generic description and does not reference any known brands or variations.
**Context:** own=Pioneer Camp

### FN #119
**Keyword:** `gerry puffer jacket`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'gerry puffer jacket' does not contain any competitor brand terms from the provided list. It is a generic description of a type of jacket and does not reference any known brands or variations.
**Context:** own=Pioneer Camp

### FN #120
**Keyword:** `lisen car phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'lisen car phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #121
**Keyword:** `nixivie magnet phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nixivie magnet phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=Jikasho

### FN #122
**Keyword:** `nixiveofficial magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nixiveofficial magnetic phone holder' does not contain any competitor brand terms from the provided list. It does not match any known brands, variations, or related terms. All words in the keyword are generic descriptors and do not refer to a specific brand.
**Context:** own=Jikasho

### FN #123
**Keyword:** `gripmaster pro 360 magnetic holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'gripmaster pro 360 magnetic holder' does not contain any competitor brand names, variations, or related terms. It is a generic description of a product without any identifiable brand references.
**Context:** own=Jikasho

### FN #124
**Keyword:** `vipbugo vacuum magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'vipbugo vacuum magnetic phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #125
**Keyword:** `msxttly vacuum magnetic phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'msxttly vacuum magnetic phone holder' does not contain any competitor brand terms from the provided list. It consists of generic descriptors and does not reference any known brands or variations.
**Context:** own=Jikasho

### FN #126
**Keyword:** `veltrix phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'veltrix phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=Jikasho

### FN #127
**Keyword:** `tenikle phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'tenikle phone holder' does not contain any competitor brand terms from the provided list. It appears to be a generic description of a product without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #128
**Keyword:** `noxive phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'noxive phone holder' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it reference any known brands in the category. All terms in the keyword are generic descriptors.
**Context:** own=Jikasho

### FN #129
**Keyword:** `vipbugo phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'vipbugo phone holder' does not contain any competitor brand terms from the provided list. It appears to be a generic product description without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #130
**Keyword:** `autobriva phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'autobriva phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=Jikasho

### FN #131
**Keyword:** `magic john phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'magic john phone holder' does not contain any competitor brand terms from the provided list. It does not match any known brands, variations, or related terms. The terms present are generic and do not refer to any specific brand.
**Context:** own=Jikasho

### FN #132
**Keyword:** `voowow phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'voowow phone holder' does not contain any competitor brand terms from the provided list. It appears to be a generic product description without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #133
**Keyword:** `eagerlyus phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'eagerlyus phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #134
**Keyword:** `kaston phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'kaston phone holder' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it reference any known brands in the category. All terms are generic descriptors without brand identification.
**Context:** own=Jikasho

### FN #135
**Keyword:** `nixiveofficial phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nixiveofficial phone holder' does not contain any competitor brand terms from the provided list. It does not match any known brands, variations, or related terms. The term 'nixiveofficial' does not correspond to any recognized competitor brand in the context of phone holders.
**Context:** own=Jikasho

### FN #136
**Keyword:** `mrglas phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'mrglas phone holder' does not contain any competitor brand terms from the provided list. It appears to be a generic description of a product without any recognizable brand names or variations.
**Context:** own=Jikasho

### FN #137
**Keyword:** `nixie phone holder`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nixie phone holder' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known brands or variations.
**Context:** own=Jikasho

### FN #138
**Keyword:** `color pop eye shadow`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'color pop eye shadow' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #139
**Keyword:** `wonderskin eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'wonderskin eye liner' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known brands or variations.
**Context:** own=REVLON

### FN #140
**Keyword:** `wetnwild eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'wetnwild eye liner' does not contain any competitor brand terms from the provided list. It appears to be a generic description of a product without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #141
**Keyword:** `mineral fusion eye pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'mineral fusion eye pencil' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #142
**Keyword:** `laura geller eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'laura geller eyeliner' does not contain any competitor brand terms from the provided list. It is a specific product name that does not match any known competitor brands or their variations. Therefore, it is classified as null.
**Context:** own=REVLON

### FN #143
**Keyword:** `laura geller eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'laura geller eye liner' does not contain any competitor brand terms from the provided list. It is a specific product name associated with the Laura Geller brand, which is not a competitor brand in this context.
**Context:** own=REVLON

### FN #144
**Keyword:** `1440 wonderskin eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword '1440 wonderskin eyeliner' does not contain any competitor brand terms from the provided list. It does not match any known brands, variations, or related terms. The term 'wonderskin' does not correspond to any recognized competitor brand in the beauty or cosmetics category.
**Context:** own=REVLON

### FN #145
**Keyword:** `nyx burnt sienna eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nyx burnt sienna eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #146
**Keyword:** `nyx brown eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nyx brown eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known competitor brands.
**Context:** own=REVLON

### FN #147
**Keyword:** `nix eye liners`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nix eye liners' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #148
**Keyword:** `color stay eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'color stay eye liner' does not contain any competitor brand terms. It is a generic description of a product type and does not reference any known brands or variations from the competitor list.
**Context:** own=REVLON

### FN #149
**Keyword:** `thrive infinity waterproof eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'thrive infinity waterproof eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #150
**Keyword:** `occasionalous 24 hr waterproof eyeliner duo sharpenable eye pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'occasionalous 24 hr waterproof eyeliner duo sharpenable eye pencil' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #151
**Keyword:** `ayky long wear gel eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'ayky long wear gel eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #152
**Keyword:** `eye embrace eyebrow pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'eye embrace eyebrow pencil' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to the product type and does not reference any known brands or variations.
**Context:** own=REVLON

### FN #153
**Keyword:** `prime eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'prime eye liner' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific brand or variation.
**Context:** own=REVLON

### FN #154
**Keyword:** `primeprometics eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'primeprometics eye liner' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it include any known brands in the cosmetics category. All terms are generic descriptors.
**Context:** own=REVLON

### FN #155
**Keyword:** `persona eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'persona eye liner' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #156
**Keyword:** `nyc jumbo eye pencil`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'nyc jumbo eye pencil' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #157
**Keyword:** `jmcy eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'jmcy eye liner' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it include any known brands in the category. All terms are generic and do not refer to a specific brand.
**Context:** own=REVLON

### FN #158
**Keyword:** `kissme eye liner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'kissme eye liner' does not contain any competitor brand terms from the provided list. It is a generic description of a product without any recognizable brand names or variations present.
**Context:** own=REVLON

### FN #159
**Keyword:** `infallible eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'infallible eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific brand or variation.
**Context:** own=REVLON

### FN #160
**Keyword:** `1440 longwear eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword '1440 longwear eyeliner' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=REVLON

### FN #161
**Keyword:** `primeeyes glide eyeliner`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'primeeyes glide eyeliner' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it include any known brands or character franchises. All terms in the keyword are generic descriptors related to the product type.
**Context:** own=REVLON

### FN #162
**Keyword:** `medela syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'medela syringes' does not contain any competitor brand terms from the provided list. 'Medela' is a recognized brand in the breastfeeding and medical supply category, but it is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Rx Crush

### FN #163
**Keyword:** `neoconnect syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neoconnect syringes' does not contain any competitor brand terms from the provided list. It appears to be a generic term without any recognizable brand names or variations present.
**Context:** own=Rx Crush

### FN #164
**Keyword:** `easy touch enfit`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch enfit' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it reference any known brands in the category. All terms are generic descriptors.
**Context:** own=Rx Crush

### FN #165
**Keyword:** `easy touch syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch syringes' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to syringes and does not reference any specific brand or variation.
**Context:** own=Rx Crush

### FN #166
**Keyword:** `syringes easytouch`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syringes easytouch' does not contain any competitor brand terms from the provided list. It consists of generic terms related to syringes and a specific product descriptor 'easytouch', which does not correspond to any known competitor brand.
**Context:** own=Rx Crush

### FN #167
**Keyword:** `boao syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'boao syringes' does not contain any competitor brand terms from the provided list. It appears to be a generic term without any recognizable brand names or variations present.
**Context:** own=Rx Crush

### FN #168
**Keyword:** `syring basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syring basik' does not contain any competitor brand terms from the provided list. It appears to be a generic term without any recognizable brand names or variations present.
**Context:** own=Rx Crush

### FN #169
**Keyword:** `basik syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'basik syringes' does not contain any competitor brand terms from the provided list. It is a generic term and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #170
**Keyword:** `basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'basik' does not contain any competitor brand terms from the provided list. It is a generic term and does not correspond to any known brand or variation.
**Context:** own=Rx Crush

### FN #171
**Keyword:** `med line syring`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'med line syring' does not contain any competitor brand terms from the provided list. It consists of generic terms related to medical supplies without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #172
**Keyword:** `medline syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'medline syringes' does not contain any competitor brand terms from the provided list. It consists of generic terms related to medical supplies without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #173
**Keyword:** `syringes med line`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syringes med line' does not contain any competitor brand terms from the provided list. All words are generic descriptors related to medical supplies and do not reference any specific brand.
**Context:** own=Rx Crush

### FN #174
**Keyword:** `easy touch`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch' does not contain any competitor brand terms from the provided list. It is a generic phrase without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #175
**Keyword:** `easy touch syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch syringe' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to syringes and does not reference any specific brand or trademarked name.
**Context:** own=Rx Crush

### FN #176
**Keyword:** `easytouch`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easytouch' does not contain any competitor brand terms from the provided list. It is a generic term and does not correspond to any known brands or variations.
**Context:** own=Rx Crush

### FN #177
**Keyword:** `neomed enfit syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neomed enfit syringe' does not contain any competitor brand terms from the provided list. It appears to be a generic description of a product without any recognizable brand names or variations present.
**Context:** own=Rx Crush

### FN #178
**Keyword:** `Captain Amera toy`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'Captain Amera toy' does not contain any competitor brand terms. It does not match any variations or related terms from the competitor brands listed. Additionally, 'Captain Amera' appears to be a misspelling or variation of 'Captain America', which is a character from Marvel, but it is not a direct brand name or recognized competitor in the context of the provided list.
**Context:** own=Transformers

### FN #179
**Keyword:** `cardinal health bed pads disposable`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health bed pads disposable' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to health and medical supplies without any identifiable brand names.
**Context:** own=Rx Crush

### FN #180
**Keyword:** `cardinal health ted stockings`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health ted stockings' does not contain any competitor brand terms from the provided list. 'Cardinal Health' is not listed as a competitor, and there are no recognizable brands or variations present in the keyword.
**Context:** own=Rx Crush

### FN #181
**Keyword:** `cardinal health adult diapers`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health adult diapers' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any specific competitor brand.
**Context:** own=Rx Crush

### FN #182
**Keyword:** `cardinal health`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'cardinal health' does not match any competitor brand terms from the provided list. It does not contain any variations or related terms of the competitors listed, nor does it reference any known brands in the category. Therefore, it is classified as null.
**Context:** own=Rx Crush

### FN #183
**Keyword:** `one care pen needles 32g 4mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles 32g 4mm' contains no competitor brand terms. It is a generic description of a product type and does not reference any known brands or variations from the competitor list.
**Context:** own=Rx Crush

### FN #184
**Keyword:** `one care pen needles`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles' does not contain any competitor brand terms from the provided list. It is purely descriptive and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #185
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles 31g 8mm' contains no competitor brand terms. It is purely descriptive of a product type and does not reference any known brands or variations from the competitor list.
**Context:** own=Rx Crush

### FN #186
**Keyword:** `neomed syrignes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neomed syrignes' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it reference any known brands in the category. All terms are generic and do not correspond to any specific brand.
**Context:** own=Rx Crush

### FN #187
**Keyword:** `neo med syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neo med syringe' does not contain any competitor brand terms from the provided list. It is a generic description of a product type and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #188
**Keyword:** `medela syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'medela syringes' does not contain any competitor brand terms from the provided list. It is a generic term referring to syringes associated with the Medela brand, which is not listed as a competitor in the provided data. Therefore, it does not qualify as a competitor brand keyword.
**Context:** own=Rx Crush

### FN #189
**Keyword:** `neoconnect syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neoconnect syringes' does not contain any competitor brand terms from the provided list. It appears to be a generic description of a product without any recognizable brand names or variations.
**Context:** own=Rx Crush

### FN #190
**Keyword:** `easy touch enfit`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch enfit' does not contain any competitor brand terms from the provided list. It does not match any variations or related terms of the competitors, nor does it reference any known brands in the category. All terms are generic descriptors without brand identification.
**Context:** own=Rx Crush

### FN #191
**Keyword:** `easy touch syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'easy touch syringes' does not contain any competitor brand terms from the provided list. It consists of generic descriptors related to syringes and does not reference any specific brand or variation.
**Context:** own=Rx Crush

### FN #192
**Keyword:** `syringes easytouch`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syringes easytouch' does not contain any competitor brand terms from the provided list. 'EasyTouch' is a product line associated with the brand 'BD', but it is not explicitly mentioned as a brand name in the keyword. Therefore, it does not qualify as a competitor brand match.
**Context:** own=Rx Crush

### FN #193
**Keyword:** `boao syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'boao syringes' does not contain any competitor brand terms from the provided list. It is a generic term and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #194
**Keyword:** `basik syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'basik syringes' does not contain any competitor brand terms from the provided list. It is a generic term and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #195
**Keyword:** `syring basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syring basik' does not contain any competitor brand terms from the provided list. It appears to be a generic term without any recognizable brand names or variations present.
**Context:** own=Rx Crush

### FN #196
**Keyword:** `basik`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'basik' does not contain any competitor brand terms from the provided list. It is a generic term and does not match any known brands or variations.
**Context:** own=Rx Crush

### FN #197
**Keyword:** `med line syring`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'med line syring' does not contain any competitor brand terms from the provided list. It consists of generic terms related to medical supplies and does not reference any specific brand or recognizable name.
**Context:** own=Rx Crush

### FN #198
**Keyword:** `medline syringes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'medline syringes' does not contain any competitor brand terms from the provided list. It consists of generic terms related to medical supplies without any identifiable brand names.
**Context:** own=Rx Crush

### FN #199
**Keyword:** `syringes med line`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'syringes med line' does not contain any competitor brand terms from the provided list. All words are generic descriptors related to medical supplies and do not reference any specific brand.
**Context:** own=Rx Crush

### FN #200
**Keyword:** `vesco enfit tip syringe 60 ml`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'vesco enfit tip syringe 60 ml' does not contain any competitor brand terms from the provided list. The term 'vesco' is not recognized as a competitor brand, and there are no other recognizable brands present in the keyword. All words are generic descriptors related to the product type.
**Context:** own=Rx Crush

### FN #201
**Keyword:** `cardinal health bed pads disposable`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health bed pads disposable' does not contain any competitor brand terms from the provided list. All words are generic descriptors related to health and medical supplies, with no identifiable brand names present.
**Context:** own=Rx Crush

### FN #202
**Keyword:** `cardinal health ted stockings`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health ted stockings' does not contain any competitor brand terms from the provided list. It is a generic description of a product and does not reference any known brands or variations.
**Context:** own=Rx Crush

### FN #203
**Keyword:** `cardinal health adult diapers`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'cardinal health adult diapers' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #204
**Keyword:** `cardinal health`
**Expected:** CB
**Model Output:** null
**Reasoning:** The keyword 'cardinal health' does not match any competitor brand terms from the provided list. It does not contain any variations or related terms of the competitors listed, nor does it reference any known brands in the category. Therefore, it is classified as null.
**Context:** own=Rx Crush

### FN #205
**Keyword:** `one care pen needles 32g 4mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles 32g 4mm' contains no competitor brand terms. It is purely descriptive of a product type and does not reference any known brands or variations from the competitor list.
**Context:** own=Rx Crush

### FN #206
**Keyword:** `one care pen needles`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles' does not contain any competitor brand terms from the provided list. It consists of generic terms related to medical supplies without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #207
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'one care pen needles 31g 8mm' contains no competitor brand terms. It is purely descriptive of a product type and does not reference any known brands or variations from the competitor list.
**Context:** own=Rx Crush

### FN #208
**Keyword:** `neomed syrignes`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neomed syrignes' does not contain any competitor brand terms from the provided list. It appears to be a generic or specific term without recognizable brand associations.
**Context:** own=Rx Crush

### FN #209
**Keyword:** `neo med syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'neo med syringe' does not contain any competitor brand terms from the provided list. It is a generic description of a product type without any identifiable brand names or variations.
**Context:** own=Rx Crush

### FN #210
**Keyword:** `vesco syringe`
**Expected:** CB
**Model Output:** null
**Reasoning:** No brand match: The keyword 'vesco syringe' does not contain any competitor brand terms from the provided list. 'Vesco' is a common name and does not match any specific competitor brand variations or related terms. Additionally, 'syringe' is a generic term for a medical device and does not indicate a brand association.
**Context:** own=Rx Crush

====================================================================================================
# M05
====================================================================================================

## M05 FALSE POSITIVES (FP): 81 errors

### FP #1
**Keyword:** `amazon renewed store`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'amazon renewed store' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a generic search term.

### FP #2
**Keyword:** `Freesipp water bottle`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'Freesipp water bottle' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a generic product search.

### FP #3
**Keyword:** `maifan sink caddy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'maifan sink caddy' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a purely generic product search.

### FP #4
**Keyword:** `ice star`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ice star' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #5
**Keyword:** `tenikle phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'tenikle phone holder' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #6
**Keyword:** `noxive phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'noxive', which is not a recognized brand in the provided lists or common hidden brands, and the rest of the terms are generic descriptors for a product type.

### FP #7
**Keyword:** `autobriva phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'autobriva', which is not recognized as a brand from the provided lists or common hidden brands, making it a generic search term.

### FP #8
**Keyword:** `voowow phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'voowow phone holder' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #9
**Keyword:** `eagerlyus phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search.

### FP #10
**Keyword:** `nixie phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'nixie phone holder' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #11
**Keyword:** `sur la table oven mitts`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'sur la table oven mitts' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #12
**Keyword:** `color stay eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'color stay eye liner' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic product search.

### FP #13
**Keyword:** `eye black amazon`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'eye black amazon' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #14
**Keyword:** `Jikashoo`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'Jikashoo' does not match any known brands from the provided lists and appears to be a generic term.

### FP #15
**Keyword:** `improvements ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'improvements ice maker' does not contain any brand names from the provided lists or recognizable hidden brands, making it a purely generic search term.

### FP #16
**Keyword:** `orgo ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'orgo ice maker' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #17
**Keyword:** `antarctic star nugget ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'nugget ice maker', which is a generic product description with no brand names detected.

### FP #18
**Keyword:** `occasionalous 24 hr waterproof eyeliner duo sharpenable eye pencil`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it describes a generic product type and features.

### FP #19
**Keyword:** `ayky long wear gel eyeliner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'eyeliner', which is a generic product term, and does not include any recognizable brand names from the provided lists or common hidden brands.

### FP #20
**Keyword:** `eye embrace eyebrow pencil`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'eyebrow pencil', which are generic product descriptors with no brand names detected.

### FP #21
**Keyword:** `color pop eye shadow`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'color pop eye shadow' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #22
**Keyword:** `prime eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'prime eye liner' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #23
**Keyword:** `persona eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'persona eye liner' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #24
**Keyword:** `jmcy eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'jmcy eye liner' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #25
**Keyword:** `infallible eyeliner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'infallible eyeliner' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic product search.

### FP #26
**Keyword:** `1440 longwear eyeliner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword '1440 longwear eyeliner' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic product search.

### FP #27
**Keyword:** `nix eye liners`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'nix eye liners' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #28
**Keyword:** `chute`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'chute' does not contain any brand names from the provided lists and is a generic term for a type of product.

### FP #29
**Keyword:** `ice flow`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ice flow' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #30
**Keyword:** `flip straw tumbler 30 oz`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'flip straw tumbler 30 oz' contains no brand names from either the brand_entities or competitor_entities lists, making it a purely generic product search.

### FP #31
**Keyword:** `flip straw tumbler 20 oz`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'flip straw tumbler 20 oz' contains no brand names from either the brand_entities or competitor_entities lists, and it describes a generic product type and feature.

### FP #32
**Keyword:** `cortland`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cortland' does not match any known brands from the provided lists and appears to be a generic term.

### FP #33
**Keyword:** `iton flask`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'iton flask' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #34
**Keyword:** `tal water bottle`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'tal water bottle' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #35
**Keyword:** `cisily sink caddy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cisily sink caddy' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic product search.

### FP #36
**Keyword:** `cisily kitchen sink caddy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cisily kitchen sink caddy' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a purely generic product search.

### FP #37
**Keyword:** `Yieach caddy sink organizer`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search.

### FP #38
**Keyword:** `woobie jacket`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'woobie jacket' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #39
**Keyword:** `transformer plush toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'transformer plush toy' contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product description.

### FP #40
**Keyword:** `green transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'green transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #41
**Keyword:** `car transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'car transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #42
**Keyword:** `pink transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'pink transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #43
**Keyword:** `soundwave transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'soundwave transformer toy' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #44
**Keyword:** `unicorn transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'unicorn transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #45
**Keyword:** `magnetic car transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'magnetic car transformer toy' contains no brand names from either the brand_entities or competitor_entities lists, and it describes a generic product type.

### FP #46
**Keyword:** `monster truck transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'monster truck transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #47
**Keyword:** `football transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'football transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #48
**Keyword:** `transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #49
**Keyword:** `barricade transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'transformer', which is a generic term for a type of toy, and 'barricade' does not reference any known brand, making it a non-branded search.

### FP #50
**Keyword:** `shockwave transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'shockwave transformer toy' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #51
**Keyword:** `bumble bee toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'bumble bee toy' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a purely generic search term.

### FP #52
**Keyword:** `bumblebee toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'bumblebee toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #53
**Keyword:** `ratchet transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ratchet transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #54
**Keyword:** `transformer car toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'transformer car toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #55
**Keyword:** `fire truck transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'fire truck transformer toy' contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product description.

### FP #56
**Keyword:** `voice activated transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'voice activated transformer toy' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #57
**Keyword:** `iron hide transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'transformer', which is a generic term for a type of toy, and 'iron hide' does not match any known brands from the provided lists or common hidden brands.

### FP #58
**Keyword:** `toy train transformer`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'toy train transformer' contains no brand names from either the brand_entities or competitor_entities lists, making it a purely generic search term.

### FP #59
**Keyword:** `helicopter transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'helicopter transformer toy' contains no brand names from either the brand_entities or competitor_entities lists, making it a purely generic product search.

### FP #60
**Keyword:** `windblade transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'transformer', which is a generic term for a type of toy, and 'windblade' does not match any known brands in the provided lists or common hidden brands.

### FP #61
**Keyword:** `starscreen transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'starscreen transformer toy' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a purely generic search term.

### FP #62
**Keyword:** `bludgeon transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'bludgeon', which is a generic term for a type of toy, and 'transformer', which refers to a category of toys, with no brand names detected.

### FP #63
**Keyword:** `scrooge transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'transformer', which is a generic term for a type of toy, and 'scrooge' does not reference any known brand or product line.

### FP #64
**Keyword:** `transformers figures`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'transformers figures' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #65
**Keyword:** `transformers action figures`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'transformers action figures' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #66
**Keyword:** `easy touch needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'easy touch needles' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic product search.

### FP #67
**Keyword:** `rx cru syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search for syringes.

### FP #68
**Keyword:** `rx syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'rx syringes' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #69
**Keyword:** `syrings rx`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'syrings rx' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #70
**Keyword:** `oven mitts amazon`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'oven mitts amazon' contains no brand names from either the brand_entities or competitor_entities lists, making it a purely generic search term.

### FP #71
**Keyword:** `large transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'large transformer toy' contains no brand names from either the brand_entities or competitor_entities lists, making it a purely generic search term.

### FP #72
**Keyword:** `giant bumblebee transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains 'transformer', which is a generic term for a type of toy, and 'giant bumblebee' does not reference any specific brand or model, making it a non-branded search.

### FP #73
**Keyword:** `cafeteria tray`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cafeteria tray' is a generic product descriptor with no brand names detected.

### FP #74
**Keyword:** `one care pen needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'one care pen needles' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a purely generic search term.

### FP #75
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search for pen needles.

### FP #76
**Keyword:** `easy touch needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'easy touch needles' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic product search.

### FP #77
**Keyword:** `rx cru syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search for syringes.

### FP #78
**Keyword:** `rx syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'rx syringes' does not contain any brand names from the provided lists or any recognizable hidden brands, making it a purely generic search term.

### FP #79
**Keyword:** `syrings rx`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'syrings rx' does not contain any recognizable brand names from the provided lists or common hidden brands, making it a generic product search.

### FP #80
**Keyword:** `one care pen needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'one care pen needles' does not contain any recognizable brand names from the provided lists or any hidden brands, making it a purely generic search term.

### FP #81
**Keyword:** `one care pen needles 31g 8mm`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword contains no brand names from either the brand_entities or competitor_entities lists, and it is a generic product search for pen needles.

## M05 FALSE NEGATIVES (FN): 15 errors

### FN #1
**Keyword:** `amazon`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'Galaxy' which is associated with Samsung, a known brand not in the provided lists.

### FN #2
**Keyword:** `magnetic iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magnetic iphone holder' contains 'iPhone', which is a brand name, thus it is not a non-branded search.

### FN #3
**Keyword:** `magnet iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magnet iphone holder' contains 'iphone', which is a brand name associated with Apple, thus it is not a non-branded search.

### FN #4
**Keyword:** `car phone holder magsafe`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'magsafe', which is a term associated with Apple's technology, indicating a branded search.

### FN #5
**Keyword:** `magsafe car phone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'magsafe', which is a term associated with Apple's technology, indicating a potential brand reference.

### FN #6
**Keyword:** `suction iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'suction iphone holder' contains 'iphone', which is a brand name, thus it is not a non-branded search.

### FN #7
**Keyword:** `iphone car holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'iPhone', which is a well-known brand name, indicating a branded search.

### FN #8
**Keyword:** `car iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'car iphone holder' contains 'iphone', which is a brand name associated with Apple, thus it is not a non-branded search.

### FN #9
**Keyword:** `iphone car holder mount`
**Expected:** NB
**Model Output:** null
**Reasoning:** Contains 'iPhone', which is a recognized brand name, thus it is not a non-branded search.

### FN #10
**Keyword:** `iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'iphone holder' contains 'iphone', which is a brand name associated with Apple, thus it is not a non-branded search.

### FN #11
**Keyword:** `portable ice maker nugget`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'nugget', which is a specific type of ice maker associated with certain brands, indicating a potential brand reference.

### FN #12
**Keyword:** `small ice maker nugget`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'nugget', which is a specific type of ice maker associated with certain brands, but does not explicitly mention any brand names from the provided lists or hidden brands.

### FN #13
**Keyword:** `termo`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword contains 'Hydro Flask', which is a recognized brand from the competitor_entities list.

### FN #14
**Keyword:** `fox oven mitts`
**Expected:** NB
**Model Output:** null
**Reasoning:** Contains 'fox', which is a known brand in the context of oven mitts, thus it is branded.

### FN #15
**Keyword:** `lego toy`
**Expected:** NB
**Model Output:** null
**Reasoning:** Contains 'lego', which is a well-known brand, making this a branded search.

====================================================================================================
# M05B
====================================================================================================

## M05B FALSE POSITIVES (FP): 57 errors

### FP #1
**Keyword:** `Yieach caddy sink organizer`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'Yieach caddy sink organizer' does not contain any brand references from the own brand or competitors. It appears to be a generic description of a product type without any identifiable brand names.

### FP #2
**Keyword:** `spider jacket men`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'spider jacket men' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of clothing for men.

### FP #3
**Keyword:** `spider jacket`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'spider jacket' does not contain any references to the own brand 'Pioneer Camp' or any of the competitors listed. It consists of generic terms describing a type of jacket without any identifiable brand names.

### FP #4
**Keyword:** `woobie jacket`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'woobie jacket' does not match any terms from the own brand or competitors, and it does not contain any recognizable brand references. It appears to be a generic term for a type of jacket.

### FP #5
**Keyword:** `msxttly vacuum magnetic phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'msxttly vacuum magnetic phone holder' does not contain any recognizable brand names or variations from the provided lists. All terms are generic descriptors of the product type and features.

### FP #6
**Keyword:** `tenikle phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'tenikle phone holder' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of product (phone holder) and a specific design (tenikle), which does not match any known brands.

### FP #7
**Keyword:** `noxive phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'noxive phone holder' does not contain any brand references from the own brand or competitors, nor does it reference any recognizable hidden brands. All terms are generic descriptors for a type of product.

### FP #8
**Keyword:** `autobriva phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'autobriva phone holder' does not contain any recognizable brand references from the own brand or competitors. It appears to be a generic term describing a type of product (phone holder) without any brand association.

### FP #9
**Keyword:** `voowow phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'voowow phone holder' does not contain any brand references from the own brand or competitors. It appears to be a generic term describing a type of product (phone holder) without any identifiable brand names.

### FP #10
**Keyword:** `eagerlyus phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'eagerlyus phone holder' does not contain any brand references from the own brand or competitors, nor does it reference any recognizable hidden brands. All terms are generic descriptors for a type of product.

### FP #11
**Keyword:** `cisiky kitchen sink caddy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cisiky kitchen sink caddy' does not contain any brand references. It consists of generic terms describing a kitchen accessory without any identifiable brand names or variations.

### FP #12
**Keyword:** `maifan sink caddy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'maifan sink caddy' contains no references to the own brand 'Cisily' or any of the competitors. All terms are generic and describe a type of product without any brand association.

### FP #13
**Keyword:** `color stay eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'color stay eye liner' does not contain any brand references. It describes a type of cosmetic product generically without mentioning any specific brand names or recognizable brand terms.

### FP #14
**Keyword:** `igloo portable ice maker countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'igloo portable ice maker countertop' contains no brand references. 'Igloo' is a common term for a type of cooler and does not refer to a specific brand in this context. The rest of the terms are generic descriptors for the product type and features.

### FP #15
**Keyword:** `aglucky ice makers countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** All terms in the keyword 'aglucky ice makers countertop' are generic descriptors for a type of product (ice makers) and do not reference any specific brand. No brand references found in the keyword or in the provided lists.

### FP #16
**Keyword:** `igloo ice makers countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'igloo ice makers countertop' contains no brand references. 'Igloo' is a common term for a type of cooler and does not refer to a specific brand in this context. The other terms are generic descriptors for the product type and features.

### FP #17
**Keyword:** `igloo ice maker countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'igloo ice maker countertop' contains no brand references. 'Igloo' is a common term for a type of cooler and does not refer to a specific brand in this context. The rest of the terms are generic descriptors for the product type and features.

### FP #18
**Keyword:** `aglucky nugget ice maker countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'aglucky nugget ice maker countertop' does not contain any brand references from the own brand or competitors. All terms are generic descriptors related to the product type and features.

### FP #19
**Keyword:** `pink igloo ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'pink igloo ice maker' does not contain any brand references from the own brand or competitors. All terms are generic descriptors for a type of product.

### FP #20
**Keyword:** `zafro ice maker countertop`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'zafro ice maker countertop' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a product type (ice maker) and its features (countertop). No hidden brands were detected either.

### FP #21
**Keyword:** `sweetcrispy countertop ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'sweetcrispy countertop ice maker' contains no brand references. All terms are generic descriptors related to the product type and features. No matches were found with the own brand or competitors, and there are no hidden brands detected.

### FP #22
**Keyword:** `igloo ice machine`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'igloo ice machine' does not contain any brand references from the own brand or competitors. 'Igloo' is a common term used to describe a type of insulated container and is not a brand in this context. Therefore, it is classified as non-branded.

### FP #23
**Keyword:** `improvements ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'improvements ice maker' contains no brand references. It consists of generic terms describing a product type and its features. No matches were found with the own brand or competitors, and there are no hidden brands detected.

### FP #24
**Keyword:** `igloo ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'igloo ice maker' does not contain any brand references. 'Igloo' is a common term used to describe a type of insulated container and is not recognized as a brand in this context. The term 'ice maker' is also generic and does not refer to any specific brand. Therefore, it is classified as non-branded.

### FP #25
**Keyword:** `orgo ice maker`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'orgo ice maker' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of product (ice maker) and does not match any known brands or brand patterns.

### FP #26
**Keyword:** `large transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'large transformer toy' does not contain any brand references. It describes a type of toy without mentioning any specific brand names or recognizable brand terms.

### FP #27
**Keyword:** `car transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'car transformer toy' does not contain any brand references. It describes a type of toy without mentioning any specific brand names or recognizable brand terms.

### FP #28
**Keyword:** `soundwave transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'soundwave transformer toy' does not contain any brand references from the own brand or competitors. The term 'transformer' could be generic in some contexts, but in this case, it is used in a non-branded manner. No hidden brands were detected either.

### FP #29
**Keyword:** `magnetic car transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'magnetic car transformer toy' does not contain any brand references from the own brand 'Transformers' or any of the competitors. All terms are generic descriptors of a type of toy and do not indicate any specific brand.

### FP #30
**Keyword:** `cafeteria tray`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'cafeteria tray' consists of generic terms describing a type of product without any brand references. It does not match any own brand or competitor brand names, variations, or related terms.

### FP #31
**Keyword:** `jmcy eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'jmcy eye liner' does not contain any recognizable brand references from the provided lists or any known hidden brands. It appears to be a generic term for a type of cosmetic product.

### FP #32
**Keyword:** `1440 longwear eyeliner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword '1440 longwear eyeliner' does not contain any brand references. It describes a type of eyeliner with a specific feature (longwear) and a quantity (1440), which are generic terms in the cosmetics category.

### FP #33
**Keyword:** `occasionalous 24 hr waterproof eyeliner duo sharpenable eye pencil`
**Expected:** null
**Model Output:** NB
**Reasoning:** All terms in the keyword are generic descriptors for a type of eyeliner product. There are no brand references found in the keyword.

### FP #34
**Keyword:** `eye embrace eyebrow pencil`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'eye embrace eyebrow pencil' does not contain any brand references from the own brand or competitors. All terms are generic descriptors related to the product type (eyebrow pencil) and do not indicate any specific brand association.

### FP #35
**Keyword:** `color pop eye shadow`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'color pop eye shadow' does not contain any brand references from the own brand (REVLON) or any competitors. It consists of generic terms describing a type of cosmetic product without any identifiable brand names.

### FP #36
**Keyword:** `prime eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'prime eye liner' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of cosmetic product without any identifiable brand names.

### FP #37
**Keyword:** `persona eye liner`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'persona eye liner' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of cosmetic product (eye liner) and a descriptor (persona) that does not indicate a specific brand.

### FP #38
**Keyword:** `mineral fusion eye pencil`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'mineral fusion eye pencil' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of cosmetic product without any identifiable brand names.

### FP #39
**Keyword:** `ice star`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ice star' does not contain any references to the own brand 'Antarctic Star' or any of the competitors. It consists of generic terms that do not indicate any brand association.

### FP #40
**Keyword:** `rx syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'rx syringes' does not contain any brand references from the own brand or competitors. It is a generic term describing a type of medical product without any identifiable brand names.

### FP #41
**Keyword:** `one care pen needles 32g 4mm`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'one care pen needles 32g 4mm' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of medical product (pen needles) and their specifications (32g, 4mm). No recognizable brands are present in the keyword.

### FP #42
**Keyword:** `one care pen needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'one care pen needles' does not contain any brand references from the own brand or competitors. It consists of generic terms related to medical supplies without any identifiable brand names.

### FP #43
**Keyword:** `ratchet transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ratchet transformer toy' does not contain any brand references. 'Ratchet' and 'toy' are generic terms, and while 'transformer' could suggest a connection to the brand 'Transformers', in this context it is used generically to describe a type of toy. No specific brand names or variations were found in the keyword.

### FP #44
**Keyword:** `fire truck transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'fire truck transformer toy' does not contain any brand references. It describes a type of toy without mentioning any specific brand names or recognizable brand terms.

### FP #45
**Keyword:** `toy train transformer`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'toy train transformer' does not contain any brand references. 'Toy' and 'train' are generic terms, and 'transformer' in this context refers to a type of toy rather than the brand 'Transformers'. No matches found with own brand or competitors.

### FP #46
**Keyword:** `helicopter transformer toy`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'helicopter transformer toy' does not contain any brand references. 'Transformer' is used generically here to describe a type of toy and is not capitalized or used in a brand context. No matches were found with the own brand or competitors.

### FP #47
**Keyword:** `easy touch needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'easy touch needles' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of product (needles) and a feature (easy touch). No hidden brands were detected either.

### FP #48
**Keyword:** `rx syringes`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'rx syringes' does not contain any brand references from the own brand or competitors. It consists of generic terms related to the product type (syringes) and a common prefix (rx) that does not indicate a specific brand.

### FP #49
**Keyword:** `one care pen needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'one care pen needles' does not contain any brand references from the own brand or competitors. It consists of generic terms related to medical supplies without any identifiable brand names.

### FP #50
**Keyword:** `easy touch needles`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'easy touch needles' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of product without any identifiable brand names.

### FP #51
**Keyword:** `sur la table oven mitts`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'sur la table oven mitts' does not contain any brand references. 'Sur la table' is a French phrase meaning 'on the table' and is not recognized as a brand in the context of oven mitts. The term 'oven mitts' is a generic product descriptor. Therefore, there are no brand references found in this keyword.

### FP #52
**Keyword:** `nixie phone holder`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'nixie phone holder' does not contain any brand references from the own brand or competitors. It consists of generic terms describing a type of phone holder without any identifiable brand names.

### FP #53
**Keyword:** `chute`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'chute' is a generic term and does not reference any specific brand or product line. It is commonly used in various contexts and does not indicate any brand association.

### FP #54
**Keyword:** `ice flow`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'ice flow' does not contain any brand references from the own brand or competitors, nor does it reference any hidden brands. It is a generic term that could describe a feature or condition related to ice, making it non-branded.

### FP #55
**Keyword:** `flip straw tumbler 30 oz`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'flip straw tumbler 30 oz' contains no brand references. It describes a type of drinkware without mentioning any specific brand names or recognizable brand patterns.

### FP #56
**Keyword:** `flip straw tumbler 20 oz`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'flip straw tumbler 20 oz' contains generic terms describing a type of drinkware and its features. There are no brand references found in the keyword.

### FP #57
**Keyword:** `tal water bottle`
**Expected:** null
**Model Output:** NB
**Reasoning:** The keyword 'tal water bottle' does not contain any brand references from the own brand or competitors. All terms are generic descriptors for a type of product.

## M05B FALSE NEGATIVES (FN): 29 errors

### FN #1
**Keyword:** `amazon`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'amazon' is a well-known brand name associated with the e-commerce platform and is not a generic term. Therefore, it contains a brand reference.

### FN #2
**Keyword:** `oven motts`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Mott's' is a well-known brand of applesauce and fruit snacks, which makes this keyword branded.

### FN #3
**Keyword:** `fox oven mitts`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Fox' is a recognized brand in the outdoor and sports apparel category, particularly known for its motocross gear and clothing. Therefore, 'fox oven mitts' contains a brand reference.

### FN #4
**Keyword:** `amazon toy`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'amazon toy' contains the brand 'Amazon', which is a recognizable brand name associated with a wide range of products, including toys.

### FN #5
**Keyword:** `amazon prime truck toy`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Amazon Prime' is a recognizable brand associated with Amazon's subscription service, and 'truck toy' does not negate the brand reference.

### FN #6
**Keyword:** `lego toy`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Lego' is a well-known brand in the toy industry, specifically known for its interlocking plastic bricks and playsets. This keyword contains a brand reference.

### FN #7
**Keyword:** `amazon ice maker`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'amazon ice maker' contains the term 'amazon', which is a recognizable brand associated with the e-commerce platform and its products. Therefore, it cannot be classified as non-branded.

### FN #8
**Keyword:** `enfit`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'enfit' is a recognized brand name associated with medical devices and feeding systems, specifically related to ENFit connectors used in healthcare. This is a brand reference, not a generic term.

### FN #9
**Keyword:** `enfit syringes`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'ENFit' is a recognized brand name associated with medical devices, specifically feeding syringes, and is not a generic term.

### FN #10
**Keyword:** `enfit`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'enfit' is a brand reference related to ENFit connectors used in medical devices, which is a recognized term in the healthcare industry.

### FN #11
**Keyword:** `enfit syringes`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'ENFit' is a recognized brand term associated with medical devices, specifically feeding syringes, and is linked to both the own brand 'Rx Crush' and the competitor 'Vesco Medical'.

### FN #12
**Keyword:** `prime eyeliner`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Prime' is a brand reference associated with Amazon's Prime service, and 'eyeliner' is a product type. The combination suggests a specific product context related to a brand.

### FN #13
**Keyword:** `magnetic iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magnetic iphone holder' contains 'iphone', which is a recognizable brand name owned by Apple. Therefore, it cannot be classified as non-branded.

### FN #14
**Keyword:** `magnet iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magnet iphone holder' contains 'iphone', which is a recognizable brand name associated with Apple. Therefore, it cannot be classified as non-branded.

### FN #15
**Keyword:** `car phone holder mag safe`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'car phone holder mag safe' contains 'mag safe', which is a term associated with Apple's MagSafe technology for iPhones, indicating a brand reference. Therefore, it is not a non-branded keyword.

### FN #16
**Keyword:** `phone holder magsafe`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'phone holder magsafe' contains 'magsafe', which is a brand reference associated with Apple's MagSafe technology for accessories. Therefore, it is not a non-branded keyword.

### FN #17
**Keyword:** `magsafe phone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magsafe phone holder' contains 'magsafe', which is a brand reference associated with Apple's MagSafe technology for phone accessories. Therefore, it cannot be classified as non-branded.

### FN #18
**Keyword:** `car phone holder magsafe`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'car phone holder magsafe' contains 'magsafe', which is a brand name associated with Apple's magnetic charging technology. Therefore, it is not a non-branded keyword.

### FN #19
**Keyword:** `magsafe car phone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magsafe car phone holder' contains 'magsafe', which is a brand name associated with Apple's MagSafe technology for accessories. Therefore, it is not a non-branded keyword.

### FN #20
**Keyword:** `magsafe phone holder car`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'magsafe phone holder car' contains 'magsafe', which is a brand reference associated with Apple's MagSafe technology for accessories. Therefore, it is not a non-branded keyword.

### FN #21
**Keyword:** `suction iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'suction iphone holder' contains 'iphone', which is a recognizable brand name owned by Apple. Therefore, it cannot be classified as non-branded.

### FN #22
**Keyword:** `car iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** The keyword 'car iphone holder' contains 'iphone', which is a recognizable brand name owned by Apple. Therefore, it cannot be classified as non-branded.

### FN #23
**Keyword:** `iphone car holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'iPhone' is a well-known brand name owned by Apple, making this keyword branded.

### FN #24
**Keyword:** `iphone car holder mount`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'iPhone' is a well-known brand name owned by Apple, making this keyword branded despite the presence of generic terms like 'car holder mount'.

### FN #25
**Keyword:** `iphone holder`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'iPhone' is a well-known brand name owned by Apple, making this keyword branded.

### FN #26
**Keyword:** `iphone holder car`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'iPhone' is a well-known brand name owned by Apple, making this keyword branded.

### FN #27
**Keyword:** `awala`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'awala' is a variation of the brand name 'Owala', which is recognized in the drinkware category.

### FN #28
**Keyword:** `cheer water bottle`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'cheer' is a common term but 'cheer water bottle' suggests a specific product type that could be associated with a brand. However, 'cheer' is not a recognized brand in the context of drinkware. The term 'water bottle' is generic, but the combination suggests a potential brand reference. Therefore, it is classified as branded due to the ambiguity of 'cheer'.

### FN #29
**Keyword:** `fahrenheit water bottle`
**Expected:** NB
**Model Output:** null
**Reasoning:** 'Fahrenheit' is a recognizable brand name associated with drinkware, specifically water bottles. This indicates a brand reference in the keyword.
