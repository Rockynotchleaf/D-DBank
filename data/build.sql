CREATE TABLE IF NOT EXISTS bank (
    IsDm integer DEFAULT 0,
    CharacterName text DEFAULT '',
    NickName text DEFAULT '',
    CopperAmt integer DEFAULT 0,
    SilverAmt integer DEFAULT 0,
    BrassAmt integer DEFAULT 0,
    GoldAmt integer DEFAULT 0,
    PlatinumAmt integer DEFAULT 0,
    ElectrumAmt integer DEFAULT 0
);