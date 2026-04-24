import os
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    async def get_user(self, user_id: int):
        response = (
            self.supabase.table("users").select("*").eq("user_id", user_id).execute()
        )
        if response.data:
            return response.data[0]
        return None

    async def create_user(self, user_id: int, first_name: str, username: str = None):
        data = {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "xp": 0,
            "rep": 0,
            "level": 1,
            "streak": 0,
        }
        return self.supabase.table("users").insert(data).execute()

    async def update_user(self, user_id: int, **kwargs):
        return (
            self.supabase.table("users").update(kwargs).eq("user_id", user_id).execute()
        )

    async def add_xp(self, user_id: int, amount: int, reason: str = "message"):
        user = await self.get_user(user_id)
        if not user:
            return None

        # Multipliers
        multiplier = 1.0
        if user.get("rep", 0) > 50:
            multiplier *= 1.2
        if user.get("streak", 0) >= 5:
            multiplier *= 1.5

        final_amount = int(amount * multiplier)
        new_xp = user["xp"] + final_amount

        # Level logic (XP for level N = 1000 * N)
        new_level = (new_xp // 1000) + 1

        update_data = {
            "xp": new_xp,
            "level": new_level,
            "last_xp_at": datetime.now(timezone.utc).isoformat(),
        }

        # Streak logic
        last_xp_str = user.get("last_xp_at")
        if last_xp_str:
            last_xp_at = datetime.fromisoformat(last_xp_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)

            # If last XP was yesterday
            if (now.date() - last_xp_at.date()) == timedelta(days=1):
                update_data["streak"] = user["streak"] + 1
            # If last XP was more than 1 day ago
            elif (now.date() - last_xp_at.date()) > timedelta(days=1):
                update_data["streak"] = 1
        else:
            update_data["streak"] = 1

        # Log XP
        self.supabase.table("xp_logs").insert(
            {"user_id": user_id, "amount": final_amount, "reason": reason}
        ).execute()

        await self.update_user(user_id, **update_data)
        return final_amount, new_level

    async def give_rep(self, from_user_id: int, to_user_id: int):
        from_user = await self.get_user(from_user_id)
        if not from_user:
            return False, "You are not registered"

        # Check limit (1 time per day)
        last_rep_str = from_user.get("last_rep_given_at")
        if last_rep_str:
            last_rep_at = datetime.fromisoformat(last_rep_str.replace("Z", "+00:00"))
            if last_rep_at.date() == datetime.now(timezone.utc).date():
                return False, "You already gave rep today"

        to_user = await self.get_user(to_user_id)
        if not to_user:
            return False, "Target user not found"

        # Log Rep
        self.supabase.table("rep_logs").insert(
            {"from_user_id": from_user_id, "to_user_id": to_user_id}
        ).execute()

        # Update user rep
        new_rep = to_user["rep"] + 1
        await self.update_user(to_user_id, rep=new_rep)

        # Update last rep given for sender
        await self.update_user(
            from_user_id, last_rep_given_at=datetime.now(timezone.utc).isoformat()
        )

        return True, "Success"

    async def create_otc_post(
        self, user_id: int, trade_type: str, item: str, price: str
    ):
        data = {
            "user_id": user_id,
            "trade_type": trade_type,
            "item": item,
            "price": price,
        }
        return self.supabase.table("otc_posts").insert(data).execute()

    async def get_leaderboard(self, limit: int = 10):
        return (
            self.supabase.table("users")
            .select("first_name, xp, streak")
            .order("xp", desc=True)
            .limit(limit)
            .execute()
        )

    async def get_secret_lots(self):
        return (
            self.supabase.table("secret_lots")
            .select("*")
            .eq("is_active", True)
            .execute()
        )

    async def buy_secret_lot(self, user_id: int, lot_id: int):
        lot_resp = (
            self.supabase.table("secret_lots").select("*").eq("id", lot_id).execute()
        )
        if not lot_resp.data:
            return False, "Lot not found"

        lot = lot_resp.data[0]
        if lot["activations_count"] >= lot.get("max_activations", 999999):
            return False, "Sold out"

        user = await self.get_user(user_id)
        if user["xp"] < lot["xp_cost"]:
            return False, "Not enough XP"

        # Deduct XP (fixed amount, no multipliers)
        new_xp = user["xp"] - lot["xp_cost"]
        await self.update_user(user_id, xp=new_xp)

        # Log buy
        self.supabase.table("secret_lot_buys").insert(
            {"lot_id": lot_id, "user_id": user_id}
        ).execute()

        # Update activation count
        self.supabase.table("secret_lots").update(
            {"activations_count": lot["activations_count"] + 1}
        ).eq("id", lot_id).execute()

        return True, "Success"
