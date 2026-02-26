UPDATE dbo.tblART
SET art_id =
    CASE
        WHEN art_id = 'J05AG-ETV' THEN 'J05AG04'
        WHEN art_id = 'J05AE-TPR' THEN 'J05AE09'
        ELSE art_id
    END
WHERE art_id IN ('J05AG-ETV', 'J05AE-TPR');
