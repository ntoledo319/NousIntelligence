import datetime
import logging
import calendar
from models import db, Budget, Expense, RecurringPayment, ExpenseCategory
from utils.doctor_appointment_helper import get_user_id_from_session

# Budget management functions
def get_budgets(session):
    """Get all budgets for the current user"""
    user_id = get_user_id_from_session(session)
    return Budget.query.filter_by(user_id=user_id).all()

def get_budget_by_id(budget_id, session):
    """Get a specific budget by ID"""
    user_id = get_user_id_from_session(session)
    return Budget.query.filter_by(id=budget_id, user_id=user_id).first()

def get_budget_by_name(name, session):
    """Get a budget by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return Budget.query.filter(
        Budget.name.ilike(f"%{name}%"),
        Budget.user_id == user_id
    ).first()

def get_budget_by_category(category, session):
    """Get a budget by category"""
    user_id = get_user_id_from_session(session)
    return Budget.query.filter_by(category=category, user_id=user_id).first()

def create_budget(name, amount, category=None, is_recurring=True, start_date=None, end_date=None, session=None):
    """Create a new budget"""
    try:
        user_id = get_user_id_from_session(session)

        # Validate category
        if category and not any(category == cat.value for cat in ExpenseCategory):
            category = ExpenseCategory.OTHER.value

        # Set default dates if not provided
        if not start_date:
            start_date = datetime.datetime.now()

        budget = Budget(
            name=name,
            amount=amount,
            category=category,
            is_recurring=is_recurring,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )

        db.session.add(budget)
        db.session.commit()
        return budget
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating budget: {str(e)}")
        return None

def update_budget(budget_id, name=None, amount=None, category=None, is_recurring=None,
                  start_date=None, end_date=None, session=None):
    """Update a budget"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the budget exists and belongs to the user
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
        if not budget:
            return None

        # Update fields if provided
        if name:
            budget.name = name
        if amount is not None:
            budget.amount = amount
        if category:
            # Validate category
            if any(category == cat.value for cat in ExpenseCategory):
                budget.category = category
        if is_recurring is not None:
            budget.is_recurring = is_recurring
        if start_date:
            budget.start_date = start_date
        if end_date:
            budget.end_date = end_date

        db.session.commit()
        return budget
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating budget: {str(e)}")
        return None

def delete_budget(budget_id, session):
    """Delete a budget"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the budget exists and belongs to the user
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
        if not budget:
            return False

        db.session.delete(budget)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting budget: {str(e)}")
        return False

def get_budget_summary(session):
    """Get a summary of all budgets for the current month"""
    user_id = get_user_id_from_session(session)

    # Get the current month's date range
    today = datetime.datetime.now()
    start_of_month = datetime.datetime(today.year, today.month, 1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end_of_month = datetime.datetime(today.year, today.month, last_day, 23, 59, 59)

    # Get all active budgets
    budgets = Budget.query.filter(
        Budget.user_id == user_id,
        (Budget.end_date.is_(None)) | (Budget.end_date >= start_of_month)
    ).all()

    # Calculate totals
    total_budget = sum(budget.amount for budget in budgets)

    # Get expenses for the current month
    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= start_of_month,
        Expense.date <= end_of_month
    ).all()

    total_spent = sum(expense.amount for expense in expenses)
    remaining = total_budget - total_spent

    # Summarize by category
    categories = {}
    for cat in ExpenseCategory:
        categories[cat.value] = {
            'budget': sum(b.amount for b in budgets if b.category == cat.value),
            'spent': sum(e.amount for e in expenses if e.category == cat.value),
            'remaining': 0
        }
        categories[cat.value]['remaining'] = categories[cat.value]['budget'] - categories[cat.value]['spent']

    return {
        'month': today.strftime('%B %Y'),
        'total_budget': total_budget,
        'total_spent': total_spent,
        'remaining': remaining,
        'percent_used': (total_spent / total_budget * 100) if total_budget > 0 else 0,
        'categories': categories
    }

# Expense management functions
def get_expenses(session, start_date=None, end_date=None, category=None):
    """Get expenses for the current user with optional filtering"""
    user_id = get_user_id_from_session(session)

    # Base query
    query = Expense.query.filter_by(user_id=user_id)

    # Apply filters if provided
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    if category:
        query = query.filter_by(category=category)

    # Sort by date, newest first
    query = query.order_by(Expense.date.desc())

    return query.all()

def get_expense_by_id(expense_id, session):
    """Get a specific expense by ID"""
    user_id = get_user_id_from_session(session)
    return Expense.query.filter_by(id=expense_id, user_id=user_id).first()

def add_expense(description, amount, date=None, category=None, payment_method=None,
                budget_name=None, is_recurring=False, recurring_frequency=None,
                next_due_date=None, notes=None, session=None):
    """Add a new expense"""
    try:
        user_id = get_user_id_from_session(session)

        # Validate category
        if category and not any(category == cat.value for cat in ExpenseCategory):
            category = ExpenseCategory.OTHER.value

        # Set default date if not provided
        if not date:
            date = datetime.datetime.now()

        # Find budget if budget_name is provided
        budget_id = None
        if budget_name:
            budget = get_budget_by_name(budget_name, session)
            if budget:
                budget_id = budget.id
            else:
                # Try to find a budget by category if name not found
                if category:
                    budget = get_budget_by_category(category, session)
                    if budget:
                        budget_id = budget.id

        expense = Expense(
            description=description,
            amount=amount,
            date=date,
            category=category,
            payment_method=payment_method,
            budget_id=budget_id,
            is_recurring=is_recurring,
            recurring_frequency=recurring_frequency,
            next_due_date=next_due_date,
            notes=notes,
            user_id=user_id
        )

        db.session.add(expense)
        db.session.commit()

        # If this is a recurring expense, create a RecurringPayment record
        if is_recurring and recurring_frequency:
            create_recurring_payment_from_expense(expense, session)

        return expense
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding expense: {str(e)}")
        return None

def update_expense(expense_id, description=None, amount=None, date=None, category=None,
                   payment_method=None, budget_name=None, is_recurring=None,
                   recurring_frequency=None, next_due_date=None, notes=None, session=None):
    """Update an expense"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the expense exists and belongs to the user
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            return None

        # Update fields if provided
        if description:
            expense.description = description
        if amount is not None:
            expense.amount = amount
        if date:
            expense.date = date
        if category:
            # Validate category
            if any(category == cat.value for cat in ExpenseCategory):
                expense.category = category
        if payment_method:
            expense.payment_method = payment_method
        if is_recurring is not None:
            expense.is_recurring = is_recurring
        if recurring_frequency:
            expense.recurring_frequency = recurring_frequency
        if next_due_date:
            expense.next_due_date = next_due_date
        if notes:
            expense.notes = notes

        # Update budget if budget_name is provided
        if budget_name:
            budget = get_budget_by_name(budget_name, session)
            if budget:
                expense.budget_id = budget.id

        db.session.commit()

        # If this is now a recurring expense, create or update RecurringPayment
        if expense.is_recurring and expense.recurring_frequency:
            create_or_update_recurring_payment_from_expense(expense, session)

        return expense
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating expense: {str(e)}")
        return None

def delete_expense(expense_id, session):
    """Delete an expense"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the expense exists and belongs to the user
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            return False

        db.session.delete(expense)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting expense: {str(e)}")
        return False

# Recurring payment functions
def get_recurring_payments(session):
    """Get all recurring payments for the current user"""
    user_id = get_user_id_from_session(session)
    return RecurringPayment.query.filter_by(user_id=user_id).all()

def get_recurring_payment_by_id(payment_id, session):
    """Get a specific recurring payment by ID"""
    user_id = get_user_id_from_session(session)
    return RecurringPayment.query.filter_by(id=payment_id, user_id=user_id).first()

def get_recurring_payment_by_name(name, session):
    """Get a recurring payment by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return RecurringPayment.query.filter(
        RecurringPayment.name.ilike(f"%{name}%"),
        RecurringPayment.user_id == user_id
    ).first()

def create_recurring_payment(name, amount, frequency, due_day=None, category=None,
                             payment_method=None, website=None, notes=None, session=None):
    """Create a new recurring payment"""
    try:
        user_id = get_user_id_from_session(session)

        # Validate category
        if category and not any(category == cat.value for cat in ExpenseCategory):
            category = ExpenseCategory.OTHER.value

        # Calculate next due date
        today = datetime.datetime.now()
        next_due_date = None

        if due_day:
            # Set due day for monthly payments
            if due_day > 28:
                # Handle cases where the day might not exist in some months
                due_day = 28

            # Find the next occurrence of this day
            year = today.year
            month = today.month

            if today.day > due_day:
                # We're past the due day this month, move to next month
                month += 1
                if month > 12:
                    month = 1
                    year += 1

            next_due_date = datetime.datetime(year, month, due_day)

        payment = RecurringPayment(
            name=name,
            amount=amount,
            frequency=frequency,
            due_day=due_day,
            category=category,
            payment_method=payment_method,
            website=website,
            next_due_date=next_due_date,
            start_date=today,
            notes=notes,
            user_id=user_id
        )

        db.session.add(payment)
        db.session.commit()
        return payment
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating recurring payment: {str(e)}")
        return None

def create_recurring_payment_from_expense(expense, session):
    """Create a recurring payment based on an expense"""
    try:
        # Extract due day if this is a monthly payment
        due_day = None
        if expense.recurring_frequency == 'monthly' and expense.date:
            due_day = expense.date.day

        return create_recurring_payment(
            name=expense.description,
            amount=expense.amount,
            frequency=expense.recurring_frequency,
            due_day=due_day,
            category=expense.category,
            payment_method=expense.payment_method,
            notes=expense.notes,
            session=session
        )
    except Exception as e:
        logging.error(f"Error creating recurring payment from expense: {str(e)}")
        return None

def create_or_update_recurring_payment_from_expense(expense, session):
    """Create or update a recurring payment based on an expense"""
    user_id = get_user_id_from_session(session)

    # Look for an existing recurring payment with the same name
    payment = RecurringPayment.query.filter(
        RecurringPayment.name.ilike(expense.description),
        RecurringPayment.user_id == user_id
    ).first()

    if payment:
        # Update existing payment
        payment.amount = expense.amount
        payment.frequency = expense.recurring_frequency
        payment.category = expense.category
        payment.payment_method = expense.payment_method
        payment.notes = expense.notes

        # Update due day if monthly
        if expense.recurring_frequency == 'monthly' and expense.date:
            payment.due_day = expense.date.day

        db.session.commit()
        return payment
    else:
        # Create new payment
        return create_recurring_payment_from_expense(expense, session)

def get_upcoming_payments(session, days=30):
    """Get recurring payments due in the next X days"""
    user_id = get_user_id_from_session(session)
    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=days)

    return RecurringPayment.query.filter(
        RecurringPayment.user_id == user_id,
        RecurringPayment.next_due_date <= end_date
    ).order_by(RecurringPayment.next_due_date).all()

def mark_payment_paid(payment_id, session):
    """Mark a recurring payment as paid and update next due date"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the payment exists and belongs to the user
        payment = RecurringPayment.query.filter_by(id=payment_id, user_id=user_id).first()
        if not payment:
            return None

        # Record this payment as an expense
        expense = Expense(
            description=payment.name,
            amount=payment.amount,
            date=datetime.datetime.now(),
            category=payment.category,
            payment_method=payment.payment_method,
            notes=f"Recurring payment: {payment.name}",
            user_id=user_id
        )

        db.session.add(expense)

        # Update next due date based on frequency
        if payment.frequency == 'monthly' and payment.due_day:
            # Calculate next month's due date
            current_date = datetime.datetime.now()
            month = current_date.month + 1
            year = current_date.year

            if month > 12:
                month = 1
                year += 1

            # Make sure we don't exceed the days in the month
            _, last_day = calendar.monthrange(year, month)
            due_day = min(payment.due_day, last_day)

            payment.next_due_date = datetime.datetime(year, month, due_day)

        elif payment.frequency == 'yearly' and payment.next_due_date:
            # Add one year to the current due date
            payment.next_due_date = payment.next_due_date.replace(year=payment.next_due_date.year + 1)

        elif payment.frequency == 'weekly' and payment.next_due_date:
            # Add one week
            payment.next_due_date = payment.next_due_date + datetime.timedelta(days=7)

        elif payment.frequency == 'daily':
            # Add one day
            payment.next_due_date = datetime.datetime.now() + datetime.timedelta(days=1)

        db.session.commit()
        return payment
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error marking payment as paid: {str(e)}")
        return None