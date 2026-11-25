from demand.ranking.signature_ranker import SignatureRanker

ranker = SignatureRanker()

print(ranker.rank().head(50))
