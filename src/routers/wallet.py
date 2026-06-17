import models
from database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/wallet", tags=["Wallet"])


class WalletCreate(BaseModel):
    user_id: int
    coins: float


class WalletResponse(WalletCreate):
    wallet_id: int

    class Config:
        from_attributes = True


@cbv(router)
class WalletAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, wallet_id: int):
        wallet = self.db.query(models.DBWallet).filter(
            models.DBWallet.wallet_id == wallet_id
        ).first()

        if wallet is None:
            raise HTTPException(status_code=404, detail="Wallet nicht gefunden")

        return wallet

    @router.get("/user/{user_id}", response_model=WalletResponse)
    def get_wallet_by_user_id(self, user_id: int):
        wallet = self.db.query(models.DBWallet).filter(
            models.DBWallet.user_id == user_id
        ).first()

        if wallet is None:
            wallet = models.DBWallet(
                user_id=user_id,
                coins=1000
            )

            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        return wallet

    @router.put("/user/{user_id}", response_model=WalletResponse)
    def update_wallet_by_user_id(self, user_id: int, wallet_data: WalletCreate):
        wallet = self.db.query(models.DBWallet).filter(
            models.DBWallet.user_id == user_id
        ).first()

        if wallet is None:
            wallet = models.DBWallet(
                user_id=user_id,
                coins=wallet_data.coins
            )
            self.db.add(wallet)
        else:
            wallet.coins = wallet_data.coins

        self.db.commit()
        self.db.refresh(wallet)

        return wallet

    @router.get("/", response_model=list[WalletResponse])
    def get_all_wallets(self):
        return self.db.query(models.DBWallet).all()

    @router.get("/{wallet_id}", response_model=WalletResponse)
    def get_wallet(self, wallet_id: int):
        return self.get_or_404(wallet_id)


    @router.post("/", response_model=WalletResponse)
    def create_wallet(self, wallet: WalletCreate):
        db_wallet = models.DBWallet(
            user_id=wallet.user_id,
            coins=wallet.coins
        )

        self.db.add(db_wallet)
        self.db.commit()
        self.db.refresh(db_wallet)

        return db_wallet

    @router.put("/{wallet_id}", response_model=WalletResponse)
    def update_wallet(self, wallet_id: int, wallet: WalletCreate):
        db_wallet = self.get_or_404(wallet_id)

        db_wallet.user_id = wallet.user_id
        db_wallet.coins = wallet.coins

        self.db.commit()
        self.db.refresh(db_wallet)

        return db_wallet

    @router.delete("/{wallet_id}")
    def delete_wallet(self, wallet_id: int):
        db_wallet = self.get_or_404(wallet_id)

        self.db.delete(db_wallet)
        self.db.commit()

        return {"message": "Wallet gelöscht"}